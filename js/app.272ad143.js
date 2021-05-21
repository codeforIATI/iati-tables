(function(t){function e(e){for(var o,s,l=e[0],i=e[1],c=e[2],u=0,p=[];u<l.length;u++)s=l[u],Object.prototype.hasOwnProperty.call(n,s)&&n[s]&&p.push(n[s][0]),n[s]=0;for(o in i)Object.prototype.hasOwnProperty.call(i,o)&&(t[o]=i[o]);d&&d(e);while(p.length)p.shift()();return r.push.apply(r,c||[]),a()}function a(){for(var t,e=0;e<r.length;e++){for(var a=r[e],o=!0,s=1;s<a.length;s++){var i=a[s];0!==n[i]&&(o=!1)}o&&(r.splice(e--,1),t=l(l.s=a[0]))}return t}var o={},n={app:0},r=[];function s(t){return l.p+"js/"+({about:"about"}[t]||t)+"."+{about:"ce8297d2"}[t]+".js"}function l(e){if(o[e])return o[e].exports;var a=o[e]={i:e,l:!1,exports:{}};return t[e].call(a.exports,a,a.exports,l),a.l=!0,a.exports}l.e=function(t){var e=[],a=n[t];if(0!==a)if(a)e.push(a[2]);else{var o=new Promise((function(e,o){a=n[t]=[e,o]}));e.push(a[2]=o);var r,i=document.createElement("script");i.charset="utf-8",i.timeout=120,l.nc&&i.setAttribute("nonce",l.nc),i.src=s(t);var c=new Error;r=function(e){i.onerror=i.onload=null,clearTimeout(u);var a=n[t];if(0!==a){if(a){var o=e&&("load"===e.type?"missing":e.type),r=e&&e.target&&e.target.src;c.message="Loading chunk "+t+" failed.\n("+o+": "+r+")",c.name="ChunkLoadError",c.type=o,c.request=r,a[1](c)}n[t]=void 0}};var u=setTimeout((function(){r({type:"timeout",target:i})}),12e4);i.onerror=i.onload=r,document.head.appendChild(i)}return Promise.all(e)},l.m=t,l.c=o,l.d=function(t,e,a){l.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:a})},l.r=function(t){"undefined"!==typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},l.t=function(t,e){if(1&e&&(t=l(t)),8&e)return t;if(4&e&&"object"===typeof t&&t&&t.__esModule)return t;var a=Object.create(null);if(l.r(a),Object.defineProperty(a,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var o in t)l.d(a,o,function(e){return t[e]}.bind(null,o));return a},l.n=function(t){var e=t&&t.__esModule?function(){return t["default"]}:function(){return t};return l.d(e,"a",e),e},l.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},l.p="/",l.oe=function(t){throw console.error(t),t};var i=window["webpackJsonp"]=window["webpackJsonp"]||[],c=i.push.bind(i);i.push=e,i=i.slice();for(var u=0;u<i.length;u++)e(i[u]);var d=c;r.push([0,"chunk-vendors"]),a()})({0:function(t,e,a){t.exports=a("56d7")},"56d7":function(t,e,a){"use strict";a.r(e);a("e260"),a("e6cf"),a("cca6"),a("a79d");var o=a("2b0e"),n=function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("v-app",[t._e(),a("v-main",[a("router-view")],1)],1)},r=[],s=a("2877"),l=a("6544"),i=a.n(l),c=a("7496"),u=a("40dc"),d=a("f6c4"),p={},f=Object(s["a"])(p,n,r,!1,null,null,null),v=f.exports;i()(f,{VApp:c["a"],VAppBar:u["a"],VMain:d["a"]});a("d3b7"),a("3ca3"),a("ddb0");var h=a("8c4f"),b=function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("v-container",[a("v-row",{attrs:{dense:!0}},[a("v-col",{attrs:{cols:"12"}},[a("v-card",{attrs:{elevation:"0",color:"white"}},[a("v-card-title",{staticClass:"capitalize-source text-h4"},[a("v-row",[a("v-col",{attrs:{xl:"2",lg:"3"}},[t._v(" IATI Tables ")]),a("v-col",{attrs:{xl:"9",lg:"9",cols:"12"}},[a("v-chip",{staticClass:"ml-3",attrs:{color:"grey darken-3","text-color":"white",href:"https://colab.research.google.com/drive/15Ahauin2YgloaFEwiGjqbnv7L91xNUua"}},[t._v(" Colab Notebook ")]),a("v-chip",{staticClass:"ml-3",attrs:{color:"deep-purple darken-4","text-color":"white",href:"https://iati.fra1.digitaloceanspaces.com/iati.sqlite.zip"}},[t._v(" SQLite Zip ")]),a("v-chip",{staticClass:"ml-3",attrs:{color:"red darken-3","text-color":"white",href:"https://iati.fra1.digitaloceanspaces.com/iati_csv.zip"}},[t._v(" CSV Zip ")]),a("v-chip",{staticClass:"ml-3",attrs:{color:"blue darken-3","text-color":"white",href:"https://iati.fra1.digitaloceanspaces.com/iati.custom.pg_dump"}},[t._v(" PG Dump (custom) ")]),a("v-chip",{staticClass:"ml-3",attrs:{color:"blue darken-2","text-color":"white",href:"https://iati.fra1.digitaloceanspaces.com/iati.dump.gz"}},[t._v(" PG Dump (gzip) ")]),a("v-chip",{staticClass:"ml-3",attrs:{color:"green darken-4","text-color":"white",href:"https://datasette.codeforiati.org"}},[t._v(" Datasette ")])],1)],1)],1)],1)],1)],1),a("v-row",{attrs:{dense:!0}},[a("v-col",{attrs:{xl:"4",cols:"12"}},[a("v-card",{attrs:{elevation:"0",color:"white"}},[a("v-card-title",[t._v(" About ")]),a("v-card-text",[a("p",[t._v("IATI data has been transfromed into tables in order to make it easier to work with relational tools. Below is the list of tables that have been created. Click on them to see the fields and types within.")]),a("p",[a("b",[t._v("Last Update:")]),t._v(" "+t._s(t.stats.updated.substring(0,16)))])])],1)],1),a("v-col",{attrs:{xl:"4",cols:"12"}},[a("v-card",{attrs:{elevation:"0",color:"white"}},[a("v-card-title",[t._v(" Output Formats ")]),a("v-card-text",[a("p",[t._v("Click on the output formats above to get the data!")]),a("p",[t._v("The Colab Notebook is an online jupyter notebook and gives you a quick way to do custom analysis on the whole of IATI data.")])])],1)],1)],1),a("v-row",{attrs:{dense:!0}},[a("v-col",{attrs:{cols:"12"}},[a("div",[a("v-card",{attrs:{elevation:"0",color:"white"}},[a("v-card-title",[t._v(" The Tables ")]),a("v-card-text",[a("p",[t._v(" Each download contains the following tables: ")]),a("v-simple-table",{attrs:{dense:!0},scopedSlots:t._u([{key:"default",fn:function(){return[a("thead",[a("tr",[a("th",{staticClass:"text-left"},[t._v(" Table Name ")]),a("th",{staticClass:"text-left"},[t._v(" Row Count ")]),a("th",{staticClass:"text-left"},[t._v(" One-to-Many Tables ")])])]),a("tbody",t._l(t.toplevel,(function(e){return a("tr",{key:e.table_name},[a("td",[a("TableModal",{attrs:{table:e,fields:t.stats.fields[e.table_name]}})],1),a("td",[t._v(t._s(e.rows.toLocaleString()))]),a("td",[a("v-row",{attrs:{dense:!0}},t._l(t.getChildren(e.table_name),(function(e){return a("v-col",{key:e.table_name,attrs:{xl:"4",lg:"6",sm:"12",xs:"12"}},[a("TableModal",{attrs:{table:e,fields:t.stats.fields[e.table_name]}}),t._v(" ("+t._s(e.rows.toLocaleString())+") ")],1)})),1)],1)])})),0)]},proxy:!0}])})],1)],1)],1)])],1)],1)},m=[],_=a("1da1"),w=(a("96cf"),a("4de4"),a("caad"),a("2532"),a("2ca0"),function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("v-dialog",{attrs:{scrollable:""},on:{input:function(e){return t.change(e)}},scopedSlots:t._u([{key:"activator",fn:function(e){var o=e.on,n=e.attrs;return[a("a",t._g(t._b({},"a",n,!1),o),[t._v(" "+t._s(t.table.table_name)+" ")])]}}]),model:{value:t.open,callback:function(e){t.open=e},expression:"open"}},[a("v-card",[a("v-card-title",{staticClass:"ml-4"},[t._v(" "+t._s(t.table.table_name)+" "),a("v-btn",{staticClass:"ml-auto",attrs:{icon:""},on:{click:function(e){return t.change(!1)}}},[a("v-icon",[t._v("mdi-close")])],1)],1),a("v-card-text",[a("v-simple-table",{attrs:{dense:!0},scopedSlots:t._u([{key:"default",fn:function(){return[a("thead",[a("tr",[a("th",{staticClass:"text-left"},[t._v(" Field ")]),a("th",{staticClass:"text-left"},[t._v(" Type ")]),a("th",{staticClass:"text-left"},[t._v(" Field Usage Count ")]),a("th",{staticClass:"text-left"},[t._v(" Docs ")])])]),a("tbody",t._l(t.fields,(function(e){return a("tr",{key:e.field},[a("td",[t._v(t._s(e.field))]),a("td",[t._v(t._s(e.type))]),a("td",[t._v(t._s(e.count.toLocaleString()))]),a("td",[t._v(t._s(e.docs))])])})),0)]},proxy:!0}])})],1)],1)],1)}),g=[],y={name:"TableModal",props:["table","fields"],data:function(){return{open:!1}},methods:{change:function(t){t&&(window.location.hash="#"+this.table.table_name),t||(this.open=!1,window.location.hash="#")}},created:function(){location.hash==="#"+this.table.table_name&&(this.open=!0)}},x=y,C=a("8336"),k=a("b0af"),T=a("99d9"),j=a("169a"),V=a("132d"),O=a("1f4f"),S=Object(s["a"])(x,w,g,!1,null,null,null),P=S.exports;i()(S,{VBtn:C["a"],VCard:k["a"],VCardText:T["a"],VCardTitle:T["b"],VDialog:j["a"],VIcon:V["a"],VSimpleTable:O["a"]});var M={name:"Home",components:{TableModal:P},data:function(){return{stats:{tables:[]}}},created:function(){this.fetchStats()},computed:{toplevel:function(){return this.stats.tables.filter((function(t){return!t.table_name.includes("_")&&t.rows>1e4}))}},methods:{fetchStats:function(){var t=Object(_["a"])(regeneratorRuntime.mark((function t(){var e,a;return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.next=2,fetch("https://iati.fra1.digitaloceanspaces.com/stats.json");case 2:return e=t.sent,t.next=5,e.json();case 5:a=t.sent,this.stats=a;case 7:case"end":return t.stop()}}),t,this)})));function e(){return t.apply(this,arguments)}return e}(),scrollDone:function(t){window.location.hash="#"+t.id},getChildren:function(t){return this.stats.tables.filter((function(e){if(t!==e.table_name)return e.table_name.startsWith(t+"_")}))}}},A=M,E=a("cc20"),L=a("62ad"),I=a("a523"),D=a("0fd9"),z=Object(s["a"])(A,b,m,!1,null,null,null),q=z.exports;i()(z,{VCard:k["a"],VCardText:T["a"],VCardTitle:T["b"],VChip:E["a"],VCol:L["a"],VContainer:I["a"],VRow:D["a"],VSimpleTable:O["a"]}),o["a"].use(h["a"]);var F=[{path:"/",name:"Home",component:q},{path:"/about",name:"About",component:function(){return a.e("about").then(a.bind(null,"f820"))}}],N=new h["a"]({mode:"history",base:"/",routes:F}),R=N,$=a("f309");o["a"].use($["a"]);var B=new $["a"]({}),G=a("f13c"),U=a.n(G);o["a"].config.productionTip=!1,o["a"].use(U.a),new o["a"]({router:R,vuetify:B,render:function(t){return t(v)}}).$mount("#app")}});
//# sourceMappingURL=app.272ad143.js.map