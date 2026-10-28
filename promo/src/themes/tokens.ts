export const C={bg:'#101c2d',ink:'#14263e',paper:'#f6f8fc',white:'#f5f8fb',muted:'#a4b5c7',teal:'#67d4b8',positive:'#087b6b',neutral:'#79889e',negative:'#bb5729',red:'#da4c42',line:'#31465a'};
export const display='Sora, sans-serif',body='Manrope, sans-serif';
export const clamp=(n:number)=>Math.max(0,Math.min(1,n));
export const smooth=(n:number)=>{n=clamp(n);return n*n*(3-2*n)};
export const ease=(f:number,a:number,b:number)=>smooth((f-a)/(b-a));
export const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
