import 'dotenv/config';
// Server/operator only. Never bundle the service-role key into public assets.
const endpoint = process.env.SUPABASE_URL;
const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
if (!endpoint || !key) throw new Error('Configure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY on the trusted operator host.');
const [command, order, award, ...reasonParts] = process.argv.slice(2);
let fn: string, args: Record<string, unknown> = {};
if (command === 'sweep') fn = 'ft_p2p_sweep';
else if (command === 'disputes') fn = 'ft_p2p_disputes';
else if (command === 'resolve') {
  if (!/^[0-9a-f-]{36}$/i.test(order || '') || !['BUYER', 'SELLER'].includes(award || '') || reasonParts.join(' ').length < 10) {
    throw new Error('Usage: p2p:support resolve ORDER_UUID BUYER|SELLER "Evidence and decision (at least 10 characters)"');
  }
  fn = 'ft_p2p_resolve'; args = { p_order: order, p_award: award, p_reason: reasonParts.join(' ') };
} else throw new Error('Choose sweep, disputes or resolve.');
const response = await fetch(new URL('/rest/v1/rpc/' + fn, endpoint), {
  method: 'POST', headers: { apikey: key, Authorization: 'Bearer ' + key, 'Content-Type': 'application/json' }, body: JSON.stringify(args),
  signal: AbortSignal.timeout(20000),
});
if (!response.ok) throw new Error('P2P operator request failed (' + response.status + '). Check service configuration and database logs.');
const result: unknown = await response.json();
console.log(command === 'disputes' ? JSON.stringify(result, null, 2) : command === 'sweep' ? `Expired ${result} unpaid orders.` : 'Dispute resolved and audited.');
