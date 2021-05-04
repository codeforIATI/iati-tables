(function(t){function e(e){for(var n,l,s=e[0],i=e[1],c=e[2],u=0,f=[];u<s.length;u++)l=s[u],Object.prototype.hasOwnProperty.call(r,l)&&r[l]&&f.push(r[l][0]),r[l]=0;for(n in i)Object.prototype.hasOwnProperty.call(i,n)&&(t[n]=i[n]);d&&d(e);while(f.length)f.shift()();return o.push.apply(o,c||[]),a()}function a(){for(var t,e=0;e<o.length;e++){for(var a=o[e],n=!0,l=1;l<a.length;l++){var i=a[l];0!==r[i]&&(n=!1)}n&&(o.splice(e--,1),t=s(s.s=a[0]))}return t}var n={},r={app:0},o=[];function l(t){return s.p+"js/"+({about:"about"}[t]||t)+"."+{about:"ce8297d2"}[t]+".js"}function s(e){if(n[e])return n[e].exports;var a=n[e]={i:e,l:!1,exports:{}};return t[e].call(a.exports,a,a.exports,s),a.l=!0,a.exports}s.e=function(t){var e=[],a=r[t];if(0!==a)if(a)e.push(a[2]);else{var n=new Promise((function(e,n){a=r[t]=[e,n]}));e.push(a[2]=n);var o,i=document.createElement("script");i.charset="utf-8",i.timeout=120,s.nc&&i.setAttribute("nonce",s.nc),i.src=l(t);var c=new Error;o=function(e){i.onerror=i.onload=null,clearTimeout(u);var a=r[t];if(0!==a){if(a){var n=e&&("load"===e.type?"missing":e.type),o=e&&e.target&&e.target.src;c.message="Loading chunk "+t+" failed.\n("+n+": "+o+")",c.name="ChunkLoadError",c.type=n,c.request=o,a[1](c)}r[t]=void 0}};var u=setTimeout((function(){o({type:"timeout",target:i})}),12e4);i.onerror=i.onload=o,document.head.appendChild(i)}return Promise.all(e)},s.m=t,s.c=n,s.d=function(t,e,a){s.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:a})},s.r=function(t){"undefined"!==typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},s.t=function(t,e){if(1&e&&(t=s(t)),8&e)return t;if(4&e&&"object"===typeof t&&t&&t.__esModule)return t;var a=Object.create(null);if(s.r(a),Object.defineProperty(a,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var n in t)s.d(a,n,function(e){return t[e]}.bind(null,n));return a},s.n=function(t){var e=t&&t.__esModule?function(){return t["default"]}:function(){return t};return s.d(e,"a",e),e},s.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},s.p="/",s.oe=function(t){throw console.error(t),t};var i=window["webpackJsonp"]=window["webpackJsonp"]||[],c=i.push.bind(i);i.push=e,i=i.slice();for(var u=0;u<i.length;u++)e(i[u]);var d=c;o.push([0,"chunk-vendors"]),a()})({0:function(t,e,a){t.exports=a("56d7")},"56d7":function(t,e,a){"use strict";a.r(e);a("e260"),a("e6cf"),a("cca6"),a("a79d");var n=a("2b0e"),r=function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("v-app",[t._e(),a("v-main",[a("router-view")],1)],1)},o=[],l=a("2877"),s=a("6544"),i=a.n(s),c=a("7496"),u=a("40dc"),d=a("f6c4"),f={},p=Object(l["a"])(f,r,o,!1,null,null,null),v=p.exports;i()(p,{VApp:c["a"],VAppBar:u["a"],VMain:d["a"]});a("d3b7"),a("3ca3"),a("ddb0");var h=a("8c4f"),b=function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("v-container",[a("v-row",{attrs:{dense:!0}},[a("v-col",{attrs:{cols:"12"}},[a("v-card",{attrs:{elevation:"0",color:"white"}},[a("v-card-title",{staticClass:"capitalize-source text-h4"},[t._v(" IATI Tables "),a("span",[a("v-chip",{staticClass:"ml-10",attrs:{color:"deep-purple darken-4","text-color":"white",href:"https://iati.fra1.digitaloceanspaces.com/iati.sqlite.zip"}},[t._v(" Download SQLite Zip ")]),a("v-chip",{staticClass:"ml-3",attrs:{color:"grey darken-3","text-color":"white",href:"https://colab.research.google.com/drive/15Ahauin2YgloaFEwiGjqbnv7L91xNUua"}},[t._v(" Link to Colab Notebook ")])],1)])],1)],1)],1),a("v-row",{attrs:{dense:!0}},[a("v-col",{attrs:{xl:"4",cols:"12"}},[a("v-card",{attrs:{elevation:"0",color:"white"}},[a("v-card-title",[t._v(" About ")]),a("v-card-text",[a("p",[t._v("IATI data has been transfromed into tables in order to make it easier to work with relational tools. Below is the list of tables that have been created. Click on them to see the fields and types within.")])])],1)],1),a("v-col",{attrs:{xl:"4",cols:"12"}},[a("v-card",{attrs:{elevation:"0",color:"white"}},[a("v-card-title",[t._v(" Output Formats ")]),a("v-card-text",[a("p",[t._v("Click on the output formats above to get the data!")])])],1)],1)],1),a("v-row",{attrs:{dense:!0}},[a("v-col",{attrs:{cols:"12"}},[a("div",[a("v-card",{attrs:{elevation:"0",color:"white"}},[a("v-card-title",[t._v(" The Tables ")]),a("v-card-text",[a("p",[t._v(" Each download contains the following tables: ")]),a("v-simple-table",{attrs:{dense:!0},scopedSlots:t._u([{key:"default",fn:function(){return[a("thead",[a("tr",[a("th",{staticClass:"text-left"},[t._v(" Table Name ")]),a("th",{staticClass:"text-left"},[t._v(" Row Count ")]),a("th",{staticClass:"text-left"},[t._v(" One-to-Many Tables ")])])]),a("tbody",t._l(t.toplevel,(function(e){return a("tr",{key:e.table_name},[a("td",[a("TableModal",{attrs:{table:e,fields:t.stats.fields[e.table_name]}})],1),a("td",[t._v(t._s(e.rows.toLocaleString()))]),a("td",[a("v-row",{attrs:{dense:!0}},t._l(t.getChildren(e.table_name),(function(e){return a("v-col",{key:e.table_name,attrs:{xl:"4",lg:"6",sm:"12",xs:"12"}},[a("TableModal",{attrs:{table:e,fields:t.stats.fields[e.table_name]}}),t._v(" ("+t._s(e.rows.toLocaleString())+") ")],1)})),1)],1)])})),0)]},proxy:!0}])})],1)],1)],1)])],1)],1)},m=[],_=a("1da1"),w=(a("96cf"),a("4de4"),a("caad"),a("2532"),a("2ca0"),function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("v-dialog",{attrs:{scrollable:""},on:{input:function(e){return t.change(e)}},scopedSlots:t._u([{key:"activator",fn:function(e){var n=e.on,r=e.attrs;return[a("a",t._g(t._b({},"a",r,!1),n),[t._v(" "+t._s(t.table.table_name)+" ")])]}}]),model:{value:t.open,callback:function(e){t.open=e},expression:"open"}},[a("v-card",[a("v-card-title",{staticClass:"ml-4"},[t._v(" "+t._s(t.table.table_name)+" "),a("v-btn",{staticClass:"ml-auto",attrs:{icon:""},on:{click:function(e){return t.change(!1)}}},[a("v-icon",[t._v("mdi-close")])],1)],1),a("v-card-text",[a("v-simple-table",{attrs:{dense:!0},scopedSlots:t._u([{key:"default",fn:function(){return[a("thead",[a("tr",[a("th",{staticClass:"text-left"},[t._v(" Field ")]),a("th",{staticClass:"text-left"},[t._v(" Type ")]),a("th",{staticClass:"text-left"},[t._v(" Field Usage Count ")]),a("th",{staticClass:"text-left"},[t._v(" Docs ")])])]),a("tbody",t._l(t.fields,(function(e){return a("tr",{key:e.field},[a("td",[t._v(t._s(e.field))]),a("td",[t._v(t._s(e.type))]),a("td",[t._v(t._s(e.count.toLocaleString()))]),a("td",[t._v(t._s(e.docs))])])})),0)]},proxy:!0}])})],1)],1)],1)}),g=[],y={name:"TableModal",props:["table","fields"],data:function(){return{open:!1}},methods:{change:function(t){t&&(window.location.hash="#"+this.table.table_name),t||(this.open=!1,window.location.hash="#")}},created:function(){location.hash==="#"+this.table.table_name&&(this.open=!0)}},x=y,C=a("8336"),T=a("b0af"),k=a("99d9"),j=a("169a"),V=a("132d"),O=a("1f4f"),S=Object(l["a"])(x,w,g,!1,null,null,null),M=S.exports;i()(S,{VBtn:C["a"],VCard:T["a"],VCardText:k["a"],VCardTitle:k["b"],VDialog:j["a"],VIcon:V["a"],VSimpleTable:O["a"]});var P={name:"Home",components:{TableModal:M},data:function(){return{stats:{tables:[]}}},created:function(){this.fetchStats()},computed:{toplevel:function(){return this.stats.tables.filter((function(t){return!t.table_name.includes("_")&&t.rows>1e5}))}},methods:{fetchStats:function(){var t=Object(_["a"])(regeneratorRuntime.mark((function t(){var e,a;return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.next=2,fetch("https://iati.fra1.digitaloceanspaces.com/stats.json");case 2:return e=t.sent,t.next=5,e.json();case 5:a=t.sent,this.stats=a;case 7:case"end":return t.stop()}}),t,this)})));function e(){return t.apply(this,arguments)}return e}(),scrollDone:function(t){window.location.hash="#"+t.id},getChildren:function(t){return this.stats.tables.filter((function(e){if(t!==e.table_name)return e.table_name.startsWith(t+"_")}))}}},A=P,E=a("cc20"),L=a("62ad"),I=a("a523"),D=a("0fd9"),F=Object(l["a"])(A,b,m,!1,null,null,null),R=F.exports;i()(F,{VCard:T["a"],VCardText:k["a"],VCardTitle:k["b"],VChip:E["a"],VCol:L["a"],VContainer:I["a"],VRow:D["a"],VSimpleTable:O["a"]}),n["a"].use(h["a"]);var $=[{path:"/",name:"Home",component:R},{path:"/about",name:"About",component:function(){return a.e("about").then(a.bind(null,"f820"))}}],q=new h["a"]({mode:"history",base:"/",routes:$}),B=q,N=a("f309");n["a"].use(N["a"]);var z=new N["a"]({}),H=a("f13c"),J=a.n(H);n["a"].config.productionTip=!1,n["a"].use(J.a),new n["a"]({router:B,vuetify:z,render:function(t){return t(v)}}).$mount("#app")}});
//# sourceMappingURL=app.2daabc01.js.map