/* Runs only against a fresh, isolated PostgreSQL cluster, never DATABASE_URL. */
const {spawnSync}=require('child_process'),fs=require('fs'),path=require('path'),assert=require('assert'),net=require('net'),{Client}=require('pg'),{randomUUID}=require('crypto');
const root=path.resolve(__dirname,'..'),bin=path.join(root,'.data','pgsql','bin'),cluster=path.join(root,'artifacts','p2p-admin-db-'+Date.now());
function command(exe,args){const r=spawnSync(path.join(bin,exe+'.exe'),args,{encoding:'utf8',windowsHide:true,stdio:'ignore'});if(r.status!==0)throw Error(exe+': '+r.stderr+' '+r.stdout);}
(async()=>{if(!fs.existsSync(path.join(bin,'initdb.exe')))throw Error('Portable PostgreSQL is required for this isolated check.');fs.mkdirSync(cluster,{recursive:true});const listener=net.createServer();await new Promise(r=>listener.listen(0,'127.0.0.1',r));const port=listener.address().port;await new Promise(r=>listener.close(r));command('initdb',['-D',cluster,'-U','postgres','-A','trust','-E','UTF8','--locale=C']);command('pg_ctl',['-D',cluster,'-l',path.join(cluster,'server.log'),'-o','-p '+port+' -h 127.0.0.1','-w','start']);
const db=new Client({host:'127.0.0.1',port,user:'postgres',database:'postgres'}),clients=[];await db.connect();
const seller='11111111-1111-4111-8111-111111111111',buyer='22222222-2222-4222-8222-222222222222',other='33333333-3333-4333-8333-333333333333';
try{
 await db.query(`create role anon;create role authenticated;create role service_role;create schema auth;create table auth.users(id uuid primary key,email text,email_confirmed_at timestamptz);create function auth.uid() returns uuid language sql as $$select nullif(current_setting('request.jwt.claim.sub',true),'')::uuid$$;create function auth.role() returns text language sql as $$select current_setting('request.jwt.claim.role',true)$$;grant usage on schema auth to anon,authenticated,service_role;create table profiles(id uuid primary key,display_name text,handle text,suspended boolean default false);create table wallets(user_id uuid primary key,balance numeric(20,2) not null check(balance>=0),locked numeric(20,2) not null check(locked>=0),updated_at timestamptz);create table admin_log(admin_id uuid,action text,target text,detail jsonb);create function public.ft_admin_note(p_action text,p_target text,p_detail jsonb) returns void language sql security definer as $$insert into admin_log values(auth.uid(),p_action,p_target,p_detail)$$;create table transactions(id bigint generated always as identity,user_id uuid,type text,label text,total numeric(20,2),balance_after numeric(20,2));`);
 await db.query(fs.readFileSync(path.join(root,'supabase','17_p2p_escrow.sql'),'utf8'));
 await db.query(fs.readFileSync(path.join(root,'supabase','17_p2p_escrow.sql'),'utf8')); // migration can be reapplied
 await db.query('insert into auth.users(id) values($1),($2),($3)',[seller,buyer,other]);await db.query('insert into profiles(id,display_name,handle) select id,\'Trader\',\'test\' from auth.users');await db.query('insert into wallets select id,1000,0,now() from auth.users');
 async function actor(id,role='authenticated'){const c=new Client({host:'127.0.0.1',port,user:'postgres',database:'postgres'});await c.connect();clients.push(c);await c.query('select set_config(\'request.jwt.claim.sub\',$1,false),set_config(\'request.jwt.claim.role\',$2,false)',[id,role]);await c.query('set role '+role);return c;}
 const s=await actor(seller),b=await actor(buyer),x=await actor(other),operator=await actor('', 'service_role');const call=async(c,fn,args=[])=>{const params=args.map((_,i)=>'$'+(i+1)).join(',');return (await c.query('select public.'+fn+'('+params+') as data',args)).rows[0].data;};
 const details={name:'Trader',provider:'Test bank',account:'TEST-ONLY-123'};
 const offerInput={key:randomUUID(),side:'SELL',currency:'USD',price:2,tokens:200,min:10,max:200,method:'Bank transfer',details};
 await assert.rejects(()=>call(s,'ft_p2p_offer',[offerInput]),/not enabled/);await db.query('update p2p_settings set live_enabled=true');
 const a=await call(s,'ft_p2p_offer',[offerInput]);assert.equal((await call(s,'ft_p2p_offer',[offerInput])).id,a.id,'Offer retries are idempotent');assert.equal(Number((await db.query('select locked from wallets where user_id=$1',[seller])).rows[0].locked),200);
 const publicMarket=await call(b,'ft_p2p_market',['USD','SELL']);assert(!JSON.stringify(publicMarket).includes('TEST-ONLY-123'),'Payment details stay private');await assert.rejects(()=>b.query('select * from p2p_orders'),/permission denied/);
 const key=randomUUID(),o=await call(b,'ft_p2p_open',[a.id,100,key,{}]);assert.equal(Number(o.tokens),50);assert.equal((await call(b,'ft_p2p_open',[a.id,100,key,{}])).id,o.id,'Order retries reserve once');
 await assert.rejects(()=>call(x,'ft_p2p_action',[o.id,'RELEASE','']),/not found/);await assert.rejects(()=>call(b,'ft_p2p_action',[o.id,'RELEASE','']),/Only the seller/);await assert.rejects(()=>call(s,'ft_p2p_action',[o.id,'RELEASE','']),/confirmed first/);
 await call(b,'ft_p2p_action',[o.id,'PAID','Test reference']);await call(b,'ft_p2p_action',[o.id,'PAID','Test reference']);await call(s,'ft_p2p_action',[o.id,'RELEASE','']);await call(s,'ft_p2p_action',[o.id,'RELEASE','']);assert.equal(Number((await db.query('select balance from wallets where user_id=$1',[buyer])).rows[0].balance),1050,'One settlement credits exactly once');
 let unpaid=await call(b,'ft_p2p_open',[a.id,20,randomUUID(),{}]);await call(b,'ft_p2p_action',[unpaid.id,'CANCEL','']);assert.equal(Number((await db.query('select available from p2p_offers where id=$1',[a.id])).rows[0].available),150,'Cancellation restores active offer inventory');
 unpaid=await call(b,'ft_p2p_open',[a.id,20,randomUUID(),{}]);await db.query('update p2p_orders set expires_at=now()-interval \'1 minute\' where id=$1',[unpaid.id]);await call(b,'ft_p2p_mine');assert.equal((await db.query('select status from p2p_orders where id=$1',[unpaid.id])).rows[0].status,'EXPIRED');
 const paid=await call(b,'ft_p2p_open',[a.id,20,randomUUID(),{}]);await call(b,'ft_p2p_action',[paid.id,'PAID','']);await db.query('update p2p_orders set expires_at=now()-interval \'1 minute\' where id=$1',[paid.id]);await call(b,'ft_p2p_mine');assert.equal((await db.query('select status from p2p_orders where id=$1',[paid.id])).rows[0].status,'PAID','Paid escrow never auto-expires');await call(s,'ft_p2p_close_offer',[a.id]);assert.equal(Number((await db.query('select locked from wallets where user_id=$1',[seller])).rows[0].locked),10,'Closing ad preserves active order escrow');
 await call(b,'ft_p2p_action',[paid.id,'DISPUTE','The payment has not been acknowledged.']);await assert.rejects(()=>call(s,'ft_p2p_action',[paid.id,'RELEASE','']),/disputed escrow/);await assert.rejects(()=>call(b,'ft_p2p_resolve',[paid.id,'BUYER','Evidence confirms payment.']),/permission denied/);await call(operator,'ft_p2p_resolve',[paid.id,'BUYER','Evidence confirms payment received.']);
 const buyAd=await call(b,'ft_p2p_offer',[{...offerInput,key:randomUUID(),side:'BUY',tokens:100,details:{}}]);const sale=await call(s,'ft_p2p_open',[buyAd.id,20,randomUUID(),details]);await call(b,'ft_p2p_action',[sale.id,'PAID','']);await call(s,'ft_p2p_action',[sale.id,'RELEASE','']);assert.equal(Number((await db.query('select locked from wallets where user_id=$1',[seller])).rows[0].locked),0);
 const refund=await call(s,'ft_p2p_open',[buyAd.id,20,randomUUID(),details]);await call(b,'ft_p2p_action',[refund.id,'PAID','']);await call(s,'ft_p2p_action',[refund.id,'DISPUTE','No incoming payment was received.']);assert.equal((await call(operator,'ft_p2p_disputes')).length,1);await call(operator,'ft_p2p_resolve',[refund.id,'SELLER','Verified that the agreed payment was not received.']);assert.equal(Number((await db.query('select locked from wallets where user_id=$1',[seller])).rows[0].locked),0,'Dispute refund returns escrow once');
 const timed=await call(s,'ft_p2p_open',[buyAd.id,20,randomUUID(),details]);await db.query("update p2p_orders set expires_at=now()-interval '1 minute' where id=$1",[timed.id]);await assert.rejects(()=>call(b,'ft_p2p_sweep'),/permission denied/);assert.equal(await call(operator,'ft_p2p_sweep'),1,'Trusted sweep expires unpaid orders without either party online');
 const small=await call(s,'ft_p2p_offer',[{...offerInput,key:randomUUID(),tokens:10,price:1,min:1,max:10}]);const simultaneous=await Promise.allSettled([call(b,'ft_p2p_open',[small.id,10,randomUUID(),{}]),call(x,'ft_p2p_open',[small.id,10,randomUUID(),{}])]);assert.equal(simultaneous.filter(r=>r.status==='fulfilled').length,1,'Concurrent buyers cannot oversell escrow');assert.equal(Number((await db.query('select sum(balance+locked) as total from wallets')).rows[0].total),3000,'FTR is conserved; P2P never mints tokens');

 await db.query(fs.readFileSync(path.join(root,'supabase','18_p2p_support_admin.sql'),'utf8'));
 await db.query(fs.readFileSync(path.join(root,'supabase','18_p2p_support_admin.sql'),'utf8'));
 const supportId='44444444-4444-4444-8444-444444444444';
 await db.query("insert into auth.users values($1,'vectorceenation@gmail.com',null)",[supportId]);
 await db.query("insert into profiles(id,display_name,handle) values($1,'Support','support')",[supportId]);
 await db.query("insert into wallets values($1,0,0,now())",[supportId]);
 const support=await actor(supportId);
 assert.equal((await call(support,'ft_admin_p2p_whoami')).allowed,false,'Unverified email cannot gain access');
 await db.query('update auth.users set email_confirmed_at=now() where id=$1',[supportId]);
 assert.equal((await call(support,'ft_admin_p2p_whoami')).allowed,true,'Verified allowlisted account gets support access');
 assert.equal((await db.query('select user_id from p2p_support_operators')).rows[0].user_id,supportId,'Role binds to account UUID');
 assert.equal((await call(b,'ft_admin_p2p_whoami')).allowed,false);
 await b.query("select set_config('request.jwt.claim.email','vectorceenation@gmail.com',false)");
 await assert.rejects(()=>call(b,'ft_admin_p2p_queue',[false]),/Support access required/,'Forged email claim has no effect');
 await assert.rejects(()=>b.query('select * from p2p_support_operators'),/permission denied/);
 await assert.rejects(()=>support.query('update p2p_settings set live_enabled=true'),/permission denied/);
 await assert.rejects(()=>call(support,'ft_p2p_resolve',[refund.id,'SELLER','Must use checked admin wrapper.']),/permission denied/);
 const adminOffer=await call(s,'ft_p2p_offer',[{...offerInput,key:randomUUID(),tokens:100,price:1,min:1,max:100}]);
 const disputed=await call(b,'ft_p2p_open',[adminOffer.id,20,randomUUID(),{}]);await call(b,'ft_p2p_action',[disputed.id,'PAID','Receipt ref']);await call(s,'ft_p2p_action',[disputed.id,'DISPUTE','I cannot locate this payment.']);
 const q=await call(support,'ft_admin_p2p_queue',[false]);assert.equal(q.open_count,1);assert.equal(Number(q.escrow_tokens),20);
 const detail=await call(support,'ft_admin_p2p_case',[disputed.id]);assert.equal(detail.payment_details.account,'TEST-ONLY-123');assert.equal(detail.messages.length,3);assert(detail.can_resolve);
 await assert.rejects(()=>call(x,'ft_admin_p2p_case',[disputed.id]),/Support access required/);
 await assert.rejects(()=>call(support,'ft_admin_p2p_resolve',[disputed.id,'BUYER',null]),/explain the evidence/);
 await assert.rejects(()=>call(support,'ft_admin_p2p_resolve',[disputed.id,'BUYER','too short']),/explain the evidence/);
 const buyerBefore=Number((await db.query('select balance from wallets where user_id=$1',[buyer])).rows[0].balance);
 const reason='Checked actual receiving account: the payment was received.';
 const decided=await call(support,'ft_admin_p2p_resolve',[disputed.id,'BUYER',reason]);assert.equal(decided.status,'COMPLETED');assert.equal(decided.decision.operator_id,supportId);
 await call(support,'ft_admin_p2p_resolve',[disputed.id,'BUYER',reason]);
 assert.equal(Number((await db.query('select balance from wallets where user_id=$1',[buyer])).rows[0].balance),buyerBefore+20,'Identical retry settles only once');
 await assert.rejects(()=>call(support,'ft_admin_p2p_resolve',[disputed.id,'SELLER',reason]),/already been resolved/);
 assert.equal((await db.query("select count(*) as n from admin_log where action='p2p.resolve'")).rows[0].n,'1');
 assert.equal((await call(support,'ft_admin_p2p_queue',[true])).orders.length,3,'History includes service-side and admin decisions');
 const disputed2=await call(b,'ft_p2p_open',[adminOffer.id,10,randomUUID(),{}]);await call(b,'ft_p2p_action',[disputed2.id,'PAID','']);await call(s,'ft_p2p_action',[disputed2.id,'DISPUTE','No incoming payment arrived.']);
 await call(support,'ft_admin_p2p_resolve',[disputed2.id,'SELLER','Reviewed bank records: no agreed payment was received.']);
 assert.equal((await call(support,'ft_admin_p2p_case',[disputed2.id])).status,'CANCELLED');
 // A support operator cannot decide a dispute involving their own account.
 const own=await call(support,'ft_p2p_open',[adminOffer.id,5,randomUUID(),{}]);await call(support,'ft_p2p_action',[own.id,'PAID','']);await call(s,'ft_p2p_action',[own.id,'DISPUTE','Support operator is my counterparty.']);
 assert.equal((await call(support,'ft_admin_p2p_case',[own.id])).can_resolve,false);
 await assert.rejects(()=>call(support,'ft_admin_p2p_resolve',[own.id,'BUYER',reason]),/your own order/);
 await db.query('update p2p_support_operators set enabled=false');await assert.rejects(()=>call(support,'ft_admin_p2p_queue',[false]),/Support access required/);
 await db.query('update p2p_support_operators set enabled=true');await db.query('update profiles set suspended=true where id=$1',[supportId]);await assert.rejects(()=>call(support,'ft_admin_p2p_queue',[false]),/suspended/);
 await db.query('update profiles set suspended=false where id=$1',[supportId]);await db.query("update auth.users set email='changed@example.com' where id=$1",[supportId]);assert.equal((await call(support,'ft_admin_p2p_whoami')).allowed,false,'Changing email revokes support access');
 assert.equal(Number((await db.query('select sum(balance+locked) as total from wallets')).rows[0].total),3000,'Admin settlement conserves token supply');
 console.log('Support SQL checks passed: verified email and UUID binding, restricted access, privacy, own-order refusal, both settlement paths, idempotency, audit trail and revocation.');
 console.log('Isolated SQL escrow checks passed: permissions, privacy, idempotency, receipt/release, cancellation, expiry, paid holds, dispute resolution, Buy/Sell roles, concurrency and supply conservation.');
}finally{for(const c of clients)await c.end();await db.end();command('pg_ctl',['-D',cluster,'-m','fast','-w','stop']);}
})().catch(e=>{console.error(e);process.exitCode=1;});
