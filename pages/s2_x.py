"""S2-X Sandbox pride and vanity page: build() writes the page. Data: assets/short.json."""
from pages._lib import *  # noqa: F401,F403


def build():
    st = step_by_code("S2-X")
    sb = json.loads((ROOT / "assets/sandbox_pride.json").read_text(encoding="utf-8"))
    words = "".join(f"<option>{E(w)}</option>" for w in sb["words"])
    one = '<p class="intro"><b>💡 In one sentence:</b> take pride, remove what vanity adds, add honor, and you land on virtue.</p>'
    body = step_head(st).replace("</h1>", "</h1>" + one, 1) + f"""<div class="card hero"><b>🪞 The idea</b><p>King − Man + Woman ≈ Queen works because one direction (male → female) is shared by many word pairs. Does a direction like <b>healthy → hollow</b> exist for pride and vanity? Try <code>vanity − pride + confidence</code>: if the direction is real, the answer should be the hollow twin of confidence (arrogance).</p></div>
<div class="card"><b>🧮 Sandbox</b><br>
<select id="xa">{words}</select> − <select id="xb">{words}</select> + <select id="xc">{words}</select>
<label><input type="checkbox" id="xex" checked> exclude the three input words (what the original experiments did)</label>
<div class="bar"><button id="xgo" class="primary">▶️ Compute</button><button id="xcopy">📋 Copy result</button></div>
<pre id="xout">Pick three words and press ▶️ Compute.</pre></div>
<h2>🧪 Test the idea (3 presets, computed live)</h2><div class="tablewrap"><table class="cmp" id="xtab"><tr><th></th><th>Equation</th><th>Expected</th><th>Top 3 (cosine)</th><th>Verdict</th></tr></table></div>
<h2>🧭 Reach virtue from vanity and pride</h2>
<div class="card hero"><p><b>Plain version:</b> vanity and virtue are far apart (they barely point the same way). Pride is already close to virtue. The gap between them is the <b>hollow, applause-hungry part</b> that vanity has and pride does not. So: <b>start at pride, take away what vanity adds, then add one good ingredient.</b> The sandbox tries every ingredient and keeps the ones that land on virtue.</p>
<div id="xreach"></div></div>
<div class="card"><b>🚶 The walk, step by step</b> <small>(pick an ingredient)</small> <select id="xing"></select><div id="xwalk"></div><div id="xbars"></div></div>
<div class="card hero"><b>⚠️ What this does and does not prove</b><ul>
<li>🛠️ These are <b>toy vectors I wrote by hand</b> on 5 dimensions ({E(", ".join(sb["dims"]))}). The arithmetic is real; the language is my judgment. A test that passes here shows the <i>mechanism</i>, not that a real model agrees.</li>
<li>📏 Preset 1 is a near tie: the expected word (arrogance) comes 3rd, within 0.01 of the winner. That is how real analogies often look: right neighbourhood, not always rank 1.</li>
<li>🪤 Untick the box: the answer becomes one of the input words. That is the known trap of the original demo.</li>
<li>🎯 "Virtue" is also one of my five dimensions, so reaching it is partly built in. The honest check is the real-model script, which now includes <code>pride − vanity + honor → virtue</code>.</li>
<li>🔬 Real test: run <code>python3 -I scripts/pride_vanity_real.py</code> (needs <code>pip install gensim</code> and downloads GloVe, about 130 MB). <b>Not run yet.</b></li></ul></div>
<h2>📖 Reading <code>pride − vanity + honor</code> word by word</h2>
<div class="card hero"><ul>
<li>🦁 <b>pride</b> = healthy self-respect: you think well of yourself because of something real. High self-regard, high "earned", mostly good.</li>
<li>🪞 <b>vanity</b> = self-regard that lives on looks and applause: high self-regard, but <i>hollow</i>, needs others' admiration, little earned, a bit negative.</li>
<li>🏅 <b>honor</b> = recognition you actually earned, with good character behind it: high "earned", high virtue.</li>
<li>🌿 <b>virtue</b> = being good in a lasting way: high "earned", high virtue, little hollowness.</li></ul>
<p><b>Why the sum makes sense:</b></p>
<ol><li>➖ <b>pride − vanity</b>: both share the same high self-regard, so that part cancels. What is left is what pride has and vanity lacks: <i>earned</i> and <i>virtue</i> up, <i>hollowness</i> and <i>needing applause</i> down. This is the "healthy, not hollow" direction, the same kind of step as man → woman in king − man + woman.</li>
<li>➕ <b>+ honor</b>: honor adds more of exactly what that direction already points to (earned, virtue). So the result becomes <i>pride without the hollow part, plus earned goodness</i>.</li>
<li>🎯 That is the everyday meaning of virtue: <b>self-respect that is earned, not shown off.</b> The nearest word to the result is virtue, which is why it lands there.</li></ol>
<div id="xexp"></div>
<small>🛠️ Same caveat as above: the numbers are my hand-written toy values, so this explains why the <i>arithmetic</i> works; whether a real model has the same shape is the GloVe test.</small></div>
<script>(function(){{var S={json.dumps(sb, ensure_ascii=False)};var W=S.words,names=Object.keys(W);
function cos(a,b){{var s=0,x=0,y=0;for(var i=0;i<a.length;i++){{s+=a[i]*b[i];x+=a[i]*a[i];y+=b[i]*b[i];}}return s/Math.sqrt(x*y)}}
function calc(a,b,c,ex){{var v=W[a].map(function(_,i){{return W[a][i]-W[b][i]+W[c][i]}});return names.filter(function(w){{return !ex||[a,b,c].indexOf(w)<0}}).map(function(w){{return [w,cos(v,W[w])]}}).sort(function(p,q){{return q[1]-p[1]}})}}
function fmt(r,n){{return r.slice(0,n).map(function(p,i){{return (i+1)+". "+p[0]+"  "+p[1].toFixed(2)}}).join("\\n")}}
var A=document.getElementById("xa"),B=document.getElementById("xb"),C=document.getElementById("xc");A.value="vanity";B.value="pride";C.value="confidence";
function run(){{var r=calc(A.value,B.value,C.value,document.getElementById("xex").checked);document.getElementById("xout").textContent=A.value+" − "+B.value+" + "+C.value+" ≈ ?\\n"+fmt(r,5)}}
document.getElementById("xgo").onclick=run;document.getElementById("xex").onchange=run;
document.getElementById("xcopy").onclick=function(){{var t=document.getElementById("xout").textContent;try{{navigator.clipboard.writeText(t);this.textContent="✅ Copied"}}catch(e){{}}}};
run();
var ING=names.filter(function(w){{return ["pride","vanity","virtue"].indexOf(w)<0}}),rec=[];
ING.forEach(function(c){{var v=W.pride.map(function(_,i){{return W.pride[i]-W.vanity[i]+W[c][i]}}),r=calc("pride","vanity",c,true);rec.push({{c:c,top:r[0][0],cv:cos(v,W.virtue)}})}});
var hit=rec.filter(function(x){{return x.top==="virtue"}}).sort(function(a,b){{return b.cv-a.cv}});
var rd=document.getElementById("xreach");
rd.innerHTML="<p>cosine to virtue: <b>vanity "+cos(W.vanity,W.virtue).toFixed(2)+"</b> (unrelated) · <b>pride "+cos(W.pride,W.virtue).toFixed(2)+"</b> (close).</p>"+(hit.length?"<ol>"+hit.slice(0,4).map(function(x){{return "<li><b>pride − vanity + "+x.c+" ≈ virtue</b> <small>("+x.cv.toFixed(2)+")</small><br>Say it: take pride, drop what vanity adds, add "+x.c+".</li>"}}).join("")+"</ol>":"<p>❌ No single ingredient lands on virtue.</p>")+"<p><small>"+hit.length+" of "+ING.length+" ingredients make virtue the nearest word.</small></p>";
var SEL=document.getElementById("xing");SEL.innerHTML=ING.map(function(c){{return "<option>"+c+"</option>"}}).join("");SEL.value=hit.length?hit[0].c:"honor";
function bars(rows){{var out="<table class='cmp'><tr><th></th>"+S.dims.map(function(d){{return "<th>"+d+"</th>"}}).join("")+"</tr>";rows.forEach(function(r){{out+="<tr><td><b>"+r[0]+"</b></td>"+r[1].map(function(x){{var w=Math.min(100,Math.abs(x)*50);return "<td><div style='height:10px;width:"+w+"%;min-width:2px;background:"+(x<0?"#e5484d":"#3fb950")+"'></div><small>"+x.toFixed(1)+"</small></td>"}}).join("")+"</tr>"}});return out+"</table><small>green = positive, red = negative; the longer, the stronger</small>"}}
function walk(){{var c=SEL.value,p=W.pride,v=W.vanity,s1=p.map(function(x,i){{return x-v[i]}}),s2=s1.map(function(x,i){{return x+W[c][i]}});
function nr(vec,ex){{var r=names.filter(function(w){{return ex.indexOf(w)<0}}).map(function(w){{return [w,cos(vec,W[w])]}}).sort(function(a,b){{return b[1]-a[1]}});return r[0][0]+" "+r[0][1].toFixed(2)}}
document.getElementById("xwalk").innerHTML="<ol><li>🧍 <b>Start at pride</b>: already "+cos(p,W.virtue).toFixed(2)+" close to virtue.</li><li>➖ <b>Take away vanity</b> (the hollow, applause part): the leftover points to <i>"+nr(s1,["pride","vanity"])+"</i>. Closeness to virtue: "+cos(s1,W.virtue).toFixed(2)+".</li><li>➕ <b>Add "+c+"</b>: nearest word is <i>"+nr(s2,["pride","vanity",c])+"</i>. Closeness to virtue: "+cos(s2,W.virtue).toFixed(2)+(nr(s2,["pride","vanity",c]).indexOf("virtue")===0?" ✅ <b>we reached virtue</b>":" ❌ not virtue")+".</li></ol>";
document.getElementById("xbars").innerHTML=bars([["vanity",v],["pride",p],["pride − vanity + "+c,s2],["virtue",W.virtue]])}}
SEL.onchange=walk;walk();
var EX=document.getElementById("xexp"),P=W.pride,V=W.vanity,H=W.honor,R=P.map(function(x,i){{return x-V[i]}}),T=R.map(function(x,i){{return x+H[i]}});EX.innerHTML=bars([["pride",P],["− vanity",V.map(function(x){{return -x}})],["= pride − vanity",R],["+ honor",H],["= result",T],["virtue (target)",W.virtue]])+"<p>cosine(result, virtue) = <b>"+cos(T,W.virtue).toFixed(2)+"</b></p>";

var tb=document.getElementById("xtab"),ok=0;S.presets.forEach(function(p){{var r=calc(p.a,p.b,p.c,true),top=r[0][0],rank=r.map(function(x){{return x[0]}}).indexOf(p.expect)+1,pass=top===p.expect;if(pass)ok++;
var tr=document.createElement("tr");tr.innerHTML="<td>"+(pass?"✅":"❌")+"</td><td>"+p.a+" − "+p.b+" + "+p.c+"<br><small>"+p.why+"</small></td><td>"+p.expect+"</td><td>"+r.slice(0,3).map(function(x){{return x[0]+" "+x[1].toFixed(2)}}).join("<br>")+"</td><td>"+(pass?"top 1":"expected is #"+rank)+"</td>";tb.appendChild(tr)}});
var s=document.createElement("p");s.innerHTML="<b>"+ok+" / "+S.presets.length+"</b> presets put the expected word first.";tb.parentNode.appendChild(s)}})();</script>""" + fb("S2-X", "🪞 Sandbox: pride & vanity, what next?")
    page("s2-x.html", "S2-X Sandbox pride and vanity", body)
