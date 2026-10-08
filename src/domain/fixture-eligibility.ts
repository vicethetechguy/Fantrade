/** Provider aliases preserve the distinction between men's and women's teams. */
export function clubKey(name: string | null | undefined): string {
  const key = String(name || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]/g, '').replace(/fc$/, '');
  const aliases: Record<string, string> = {manutd:'manchesterunited',manunited:'manchesterunited',mancity:'manchestercity',spurs:'tottenhamhotspur',tottenham:'tottenhamhotspur',barca:'barcelona',fcbarcelona:'barcelona',psg:'parissaintgermain',barcelonafemeni:'barcelonawomen',barcelonafemenino:'barcelonawomen'};
  return aliases[key] || key;
}
export function clubInFixture(club: string | null | undefined, home: string, away: string): boolean {
  const team = clubKey(club);
  return !!team && !['pro','club','coach','unknown'].includes(team) && (team === clubKey(home) || team === clubKey(away));
}
