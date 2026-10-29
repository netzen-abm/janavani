"""Responsive design tokens and CSS for the independent Dynamic Web surface."""

DYNAMIC_WEB_STYLES = r"""
:root{color-scheme:light;--navy:#071d30;--blue:#184966;--gold:#d6a34a;--paper:#f5f2e9;--ink:#172d3c;--muted:#5c6d78;--line:rgba(23,45,60,.16)}
*{box-sizing:border-box}
body{margin:0;background:#fffdf8;color:var(--ink);font:16px/1.65 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
a{color:var(--blue);text-underline-offset:.18em}
a:focus-visible,button:focus-visible,select:focus-visible{outline:3px solid var(--gold);outline-offset:3px}
.site-header{background:var(--navy);color:#fff;padding:14px 22px}
.header-inner,.wrap{width:min(1120px,calc(100% - 36px));margin:0 auto}
.header-inner{display:flex;align-items:center;justify-content:space-between;gap:24px}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;letter-spacing:.08em;color:#fff;text-decoration:none}.brand img{display:block;width:34px;height:34px;flex:0 0 34px}
.nav{display:flex;gap:18px;flex-wrap:wrap}
.nav a{color:#fff;font-size:.9rem}
main{min-height:70vh}
.hero{background:var(--navy);color:#fff;padding:clamp(54px,9vw,108px) 0}
.eyebrow{margin:0 0 14px;color:#ead3a1;font-size:.75rem;font-weight:800;letter-spacing:.16em;text-transform:uppercase}
h1,h2,h3{line-height:1.12;letter-spacing:-.035em}
h1{max-width:850px;font-size:clamp(2.5rem,7vw,5.7rem);margin:0 0 22px}
h2{font-size:clamp(1.7rem,4vw,2.8rem)}
.lead{max-width:760px;color:rgba(255,255,255,.84);font-size:clamp(1.05rem,2vw,1.25rem)}
.actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:28px}
.button,button{
 display:inline-block;border:1px solid var(--gold);border-radius:8px;
 background:var(--gold);color:#172d3c;padding:11px 16px;
 font:inherit;font-weight:750;text-decoration:none;cursor:pointer
}
.button.secondary{background:transparent;color:#fff;border-color:rgba(255,255,255,.45)}
.section{padding:clamp(45px,7vw,78px) 0}
.intro{max-width:780px}
.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:24px}
.card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:22px}
.card p{color:var(--muted)}
.pathway-box{margin-top:28px;padding:clamp(20px,4vw,32px);background:var(--paper);border:1px solid var(--line);border-radius:14px}
label{display:block;font-weight:700;margin:14px 0 7px}
select{width:100%;max-width:620px;padding:12px;border:1px solid #778793;border-radius:7px;background:#fff;font:inherit}
.hint{font-size:.9rem;color:var(--muted)}
footer{background:#edf0f0;padding:28px 0;color:#485b68;font-size:.9rem}
@media(max-width:760px){.header-inner{align-items:flex-start;flex-direction:column}.grid{grid-template-columns:1fr}.nav{gap:12px}.hero{padding:54px 0}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{scroll-behavior:auto!important;animation:none!important;transition:none!important}}
"""
