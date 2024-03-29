/*! For license information please see main.js.LICENSE.txt */
(()=>{"use strict";const t=window,e=t.ShadowRoot&&(void 0===t.ShadyCSS||t.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,i=Symbol(),o=new WeakMap;class s{constructor(t,e,o){if(this._$cssResult$=!0,o!==i)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const i=this.t;if(e&&void 0===t){const e=void 0!==i&&1===i.length;e&&(t=o.get(i)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),e&&o.set(i,t))}return t}toString(){return this.cssText}}const r=(t,...e)=>{const o=1===t.length?t[0]:e.reduce(((e,i,o)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[o+1]),t[0]);return new s(o,t,i)},n=e?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new s("string"==typeof t?t:t+"",void 0,i))(e)})(t):t;var a;const l=window,d=l.trustedTypes,c=d?d.emptyScript:"",h=l.reactiveElementPolyfillSupport,u={toAttribute(t,e){switch(e){case Boolean:t=t?c:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},p=(t,e)=>e!==t&&(e==e||t==t),b={attribute:!0,type:String,converter:u,reflect:!1,hasChanged:p};class f extends HTMLElement{constructor(){super(),this._$Ei=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$El=null,this.u()}static addInitializer(t){var e;this.finalize(),(null!==(e=this.h)&&void 0!==e?e:this.h=[]).push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach(((e,i)=>{const o=this._$Ep(i,e);void 0!==o&&(this._$Ev.set(o,i),t.push(o))})),t}static createProperty(t,e=b){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const i="symbol"==typeof t?Symbol():"__"+t,o=this.getPropertyDescriptor(t,i,e);void 0!==o&&Object.defineProperty(this.prototype,t,o)}}static getPropertyDescriptor(t,e,i){return{get(){return this[e]},set(o){const s=this[t];this[e]=o,this.requestUpdate(t,s,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||b}static finalize(){if(this.hasOwnProperty("finalized"))return!1;this.finalized=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),void 0!==t.h&&(this.h=[...t.h]),this.elementProperties=new Map(t.elementProperties),this._$Ev=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const i of e)this.createProperty(i,t[i])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(n(t))}else void 0!==t&&e.push(n(t));return e}static _$Ep(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}u(){var t;this._$E_=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$Eg(),this.requestUpdate(),null===(t=this.constructor.h)||void 0===t||t.forEach((t=>t(this)))}addController(t){var e,i;(null!==(e=this._$ES)&&void 0!==e?e:this._$ES=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(i=t.hostConnected)||void 0===i||i.call(t))}removeController(t){var e;null===(e=this._$ES)||void 0===e||e.splice(this._$ES.indexOf(t)>>>0,1)}_$Eg(){this.constructor.elementProperties.forEach(((t,e)=>{this.hasOwnProperty(e)&&(this._$Ei.set(e,this[e]),delete this[e])}))}createRenderRoot(){var i;const o=null!==(i=this.shadowRoot)&&void 0!==i?i:this.attachShadow(this.constructor.shadowRootOptions);return((i,o)=>{e?i.adoptedStyleSheets=o.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet)):o.forEach((e=>{const o=document.createElement("style"),s=t.litNonce;void 0!==s&&o.setAttribute("nonce",s),o.textContent=e.cssText,i.appendChild(o)}))})(o,this.constructor.elementStyles),o}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$ES)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)}))}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$ES)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)}))}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$EO(t,e,i=b){var o;const s=this.constructor._$Ep(t,i);if(void 0!==s&&!0===i.reflect){const r=(void 0!==(null===(o=i.converter)||void 0===o?void 0:o.toAttribute)?i.converter:u).toAttribute(e,i.type);this._$El=t,null==r?this.removeAttribute(s):this.setAttribute(s,r),this._$El=null}}_$AK(t,e){var i;const o=this.constructor,s=o._$Ev.get(t);if(void 0!==s&&this._$El!==s){const t=o.getPropertyOptions(s),r="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==(null===(i=t.converter)||void 0===i?void 0:i.fromAttribute)?t.converter:u;this._$El=s,this[s]=r.fromAttribute(e,t.type),this._$El=null}}requestUpdate(t,e,i){let o=!0;void 0!==t&&(((i=i||this.constructor.getPropertyOptions(t)).hasChanged||p)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===i.reflect&&this._$El!==t&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(t,i))):o=!1),!this.isUpdatePending&&o&&(this._$E_=this._$Ej())}async _$Ej(){this.isUpdatePending=!0;try{await this._$E_}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Ei&&(this._$Ei.forEach(((t,e)=>this[e]=t)),this._$Ei=void 0);let e=!1;const i=this._$AL;try{e=this.shouldUpdate(i),e?(this.willUpdate(i),null===(t=this._$ES)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)})),this.update(i)):this._$Ek()}catch(t){throw e=!1,this._$Ek(),t}e&&this._$AE(i)}willUpdate(t){}_$AE(t){var e;null===(e=this._$ES)||void 0===e||e.forEach((t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$Ek(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$E_}shouldUpdate(t){return!0}update(t){void 0!==this._$EC&&(this._$EC.forEach(((t,e)=>this._$EO(e,this[e],t))),this._$EC=void 0),this._$Ek()}updated(t){}firstUpdated(t){}}var v;f.finalized=!0,f.elementProperties=new Map,f.elementStyles=[],f.shadowRootOptions={mode:"open"},null==h||h({ReactiveElement:f}),(null!==(a=l.reactiveElementVersions)&&void 0!==a?a:l.reactiveElementVersions=[]).push("1.5.0");const m=window,g=m.trustedTypes,y=g?g.createPolicy("lit-html",{createHTML:t=>t}):void 0,w=`lit$${(Math.random()+"").slice(9)}$`,_="?"+w,$=`<${_}>`,x=document,k=(t="")=>x.createComment(t),A=t=>null===t||"object"!=typeof t&&"function"!=typeof t,C=Array.isArray,E=t=>C(t)||"function"==typeof(null==t?void 0:t[Symbol.iterator]),S=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,T=/-->/g,z=/>/g,P=RegExp(">|[ \t\n\f\r](?:([^\\s\"'>=/]+)([ \t\n\f\r]*=[ \t\n\f\r]*(?:[^ \t\n\f\r\"'`<>=]|(\"|')|))|$)","g"),L=/'/g,I=/"/g,O=/^(?:script|style|textarea|title)$/i,D=t=>(e,...i)=>({_$litType$:t,strings:e,values:i}),R=D(1),U=(D(2),Symbol.for("lit-noChange")),F=Symbol.for("lit-nothing"),B=new WeakMap,H=x.createTreeWalker(x,129,null,!1),M=(t,e)=>{const i=t.length-1,o=[];let s,r=2===e?"<svg>":"",n=S;for(let e=0;e<i;e++){const i=t[e];let a,l,d=-1,c=0;for(;c<i.length&&(n.lastIndex=c,l=n.exec(i),null!==l);)c=n.lastIndex,n===S?"!--"===l[1]?n=T:void 0!==l[1]?n=z:void 0!==l[2]?(O.test(l[2])&&(s=RegExp("</"+l[2],"g")),n=P):void 0!==l[3]&&(n=P):n===P?">"===l[0]?(n=null!=s?s:S,d=-1):void 0===l[1]?d=-2:(d=n.lastIndex-l[2].length,a=l[1],n=void 0===l[3]?P:'"'===l[3]?I:L):n===I||n===L?n=P:n===T||n===z?n=S:(n=P,s=void 0);const h=n===P&&t[e+1].startsWith("/>")?" ":"";r+=n===S?i+$:d>=0?(o.push(a),i.slice(0,d)+"$lit$"+i.slice(d)+w+h):i+w+(-2===d?(o.push(void 0),e):h)}const a=r+(t[i]||"<?>")+(2===e?"</svg>":"");if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return[void 0!==y?y.createHTML(a):a,o]};class N{constructor({strings:t,_$litType$:e},i){let o;this.parts=[];let s=0,r=0;const n=t.length-1,a=this.parts,[l,d]=M(t,e);if(this.el=N.createElement(l,i),H.currentNode=this.el.content,2===e){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(o=H.nextNode())&&a.length<n;){if(1===o.nodeType){if(o.hasAttributes()){const t=[];for(const e of o.getAttributeNames())if(e.endsWith("$lit$")||e.startsWith(w)){const i=d[r++];if(t.push(e),void 0!==i){const t=o.getAttribute(i.toLowerCase()+"$lit$").split(w),e=/([.?@])?(.*)/.exec(i);a.push({type:1,index:s,name:e[2],strings:t,ctor:"."===e[1]?K:"?"===e[1]?G:"@"===e[1]?Z:W})}else a.push({type:6,index:s})}for(const e of t)o.removeAttribute(e)}if(O.test(o.tagName)){const t=o.textContent.split(w),e=t.length-1;if(e>0){o.textContent=g?g.emptyScript:"";for(let i=0;i<e;i++)o.append(t[i],k()),H.nextNode(),a.push({type:2,index:++s});o.append(t[e],k())}}}else if(8===o.nodeType)if(o.data===_)a.push({type:2,index:s});else{let t=-1;for(;-1!==(t=o.data.indexOf(w,t+1));)a.push({type:7,index:s}),t+=w.length-1}s++}}static createElement(t,e){const i=x.createElement("template");return i.innerHTML=t,i}}function V(t,e,i=t,o){var s,r,n,a;if(e===U)return e;let l=void 0!==o?null===(s=i._$Co)||void 0===s?void 0:s[o]:i._$Cl;const d=A(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==d&&(null===(r=null==l?void 0:l._$AO)||void 0===r||r.call(l,!1),void 0===d?l=void 0:(l=new d(t),l._$AT(t,i,o)),void 0!==o?(null!==(n=(a=i)._$Co)&&void 0!==n?n:a._$Co=[])[o]=l:i._$Cl=l),void 0!==l&&(e=V(t,l._$AS(t,e.values),l,o)),e}class j{constructor(t,e){this.u=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}v(t){var e;const{el:{content:i},parts:o}=this._$AD,s=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:x).importNode(i,!0);H.currentNode=s;let r=H.nextNode(),n=0,a=0,l=o[0];for(;void 0!==l;){if(n===l.index){let e;2===l.type?e=new q(r,r.nextSibling,this,t):1===l.type?e=new l.ctor(r,l.name,l.strings,this,t):6===l.type&&(e=new X(r,this,t)),this.u.push(e),l=o[++a]}n!==(null==l?void 0:l.index)&&(r=H.nextNode(),n++)}return s}p(t){let e=0;for(const i of this.u)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}}class q{constructor(t,e,i,o){var s;this.type=2,this._$AH=F,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=o,this._$Cm=null===(s=null==o?void 0:o.isConnected)||void 0===s||s}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cm}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=V(this,t,e),A(t)?t===F||null==t||""===t?(this._$AH!==F&&this._$AR(),this._$AH=F):t!==this._$AH&&t!==U&&this.g(t):void 0!==t._$litType$?this.$(t):void 0!==t.nodeType?this.T(t):E(t)?this.k(t):this.g(t)}O(t,e=this._$AB){return this._$AA.parentNode.insertBefore(t,e)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}g(t){this._$AH!==F&&A(this._$AH)?this._$AA.nextSibling.data=t:this.T(x.createTextNode(t)),this._$AH=t}$(t){var e;const{values:i,_$litType$:o}=t,s="number"==typeof o?this._$AC(t):(void 0===o.el&&(o.el=N.createElement(o.h,this.options)),o);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===s)this._$AH.p(i);else{const t=new j(s,this),e=t.v(this.options);t.p(i),this.T(e),this._$AH=t}}_$AC(t){let e=B.get(t.strings);return void 0===e&&B.set(t.strings,e=new N(t)),e}k(t){C(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let i,o=0;for(const s of t)o===e.length?e.push(i=new q(this.O(k()),this.O(k()),this,this.options)):i=e[o],i._$AI(s),o++;o<e.length&&(this._$AR(i&&i._$AB.nextSibling,o),e.length=o)}_$AR(t=this._$AA.nextSibling,e){var i;for(null===(i=this._$AP)||void 0===i||i.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cm=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}}class W{constructor(t,e,i,o,s){this.type=1,this._$AH=F,this._$AN=void 0,this.element=t,this.name=e,this._$AM=o,this.options=s,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=F}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,i,o){const s=this.strings;let r=!1;if(void 0===s)t=V(this,t,e,0),r=!A(t)||t!==this._$AH&&t!==U,r&&(this._$AH=t);else{const o=t;let n,a;for(t=s[0],n=0;n<s.length-1;n++)a=V(this,o[i+n],e,n),a===U&&(a=this._$AH[n]),r||(r=!A(a)||a!==this._$AH[n]),a===F?t=F:t!==F&&(t+=(null!=a?a:"")+s[n+1]),this._$AH[n]=a}r&&!o&&this.j(t)}j(t){t===F?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}}class K extends W{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===F?void 0:t}}const Y=g?g.emptyScript:"";class G extends W{constructor(){super(...arguments),this.type=4}j(t){t&&t!==F?this.element.setAttribute(this.name,Y):this.element.removeAttribute(this.name)}}class Z extends W{constructor(t,e,i,o,s){super(t,e,i,o,s),this.type=5}_$AI(t,e=this){var i;if((t=null!==(i=V(this,t,e,0))&&void 0!==i?i:F)===U)return;const o=this._$AH,s=t===F&&o!==F||t.capture!==o.capture||t.once!==o.once||t.passive!==o.passive,r=t!==F&&(o===F||s);s&&this.element.removeEventListener(this.name,this,o),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,i;"function"==typeof this._$AH?this._$AH.call(null!==(i=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==i?i:this.element,t):this._$AH.handleEvent(t)}}class X{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){V(this,t)}}const J={P:"$lit$",A:w,M:_,C:1,L:M,R:j,D:E,V,I:q,H:W,N:G,U:Z,B:K,F:X},Q=m.litHtmlPolyfillSupport;var tt,et;null==Q||Q(N,q),(null!==(v=m.litHtmlVersions)&&void 0!==v?v:m.litHtmlVersions=[]).push("2.5.0");class it extends f{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var t,e;const i=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=i.firstChild),i}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,i)=>{var o,s;const r=null!==(o=null==i?void 0:i.renderBefore)&&void 0!==o?o:e;let n=r._$litPart$;if(void 0===n){const t=null!==(s=null==i?void 0:i.renderBefore)&&void 0!==s?s:null;r._$litPart$=n=new q(e.insertBefore(k(),t),t,void 0,null!=i?i:{})}return n._$AI(t),n})(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!1)}render(){return U}}it.finalized=!0,it._$litElement$=!0,null===(tt=globalThis.litElementHydrateSupport)||void 0===tt||tt.call(globalThis,{LitElement:it});const ot=globalThis.litElementPolyfillSupport;null==ot||ot({LitElement:it}),(null!==(et=globalThis.litElementVersions)&&void 0!==et?et:globalThis.litElementVersions=[]).push("3.2.2");var st,rt,nt=window,at=nt.ShadowRoot&&(void 0===nt.ShadyCSS||nt.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,lt=Symbol(),dt=new WeakMap,ct=class{constructor(t,e,i){if(this._$cssResult$=!0,i!==lt)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(at&&void 0===t){const i=void 0!==e&&1===e.length;i&&(t=dt.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),i&&dt.set(e,t))}return t}toString(){return this.cssText}},ht=(t,...e)=>{const i=1===t.length?t[0]:e.reduce(((e,i,o)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[o+1]),t[0]);return new ct(i,t,lt)},ut=at?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new ct("string"==typeof t?t:t+"",void 0,lt))(e)})(t):t,pt=window,bt=pt.trustedTypes,ft=bt?bt.emptyScript:"",vt=pt.reactiveElementPolyfillSupport,mt={toAttribute(t,e){switch(e){case Boolean:t=t?ft:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},gt=(t,e)=>e!==t&&(e==e||t==t),yt={attribute:!0,type:String,converter:mt,reflect:!1,hasChanged:gt},wt=class extends HTMLElement{constructor(){super(),this._$Ei=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$El=null,this.u()}static addInitializer(t){var e;this.finalize(),(null!==(e=this.h)&&void 0!==e?e:this.h=[]).push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach(((e,i)=>{const o=this._$Ep(i,e);void 0!==o&&(this._$Ev.set(o,i),t.push(o))})),t}static createProperty(t,e=yt){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const i="symbol"==typeof t?Symbol():"__"+t,o=this.getPropertyDescriptor(t,i,e);void 0!==o&&Object.defineProperty(this.prototype,t,o)}}static getPropertyDescriptor(t,e,i){return{get(){return this[e]},set(o){const s=this[t];this[e]=o,this.requestUpdate(t,s,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||yt}static finalize(){if(this.hasOwnProperty("finalized"))return!1;this.finalized=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),void 0!==t.h&&(this.h=[...t.h]),this.elementProperties=new Map(t.elementProperties),this._$Ev=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const i of e)this.createProperty(i,t[i])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(ut(t))}else void 0!==t&&e.push(ut(t));return e}static _$Ep(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}u(){var t;this._$E_=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$Eg(),this.requestUpdate(),null===(t=this.constructor.h)||void 0===t||t.forEach((t=>t(this)))}addController(t){var e,i;(null!==(e=this._$ES)&&void 0!==e?e:this._$ES=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(i=t.hostConnected)||void 0===i||i.call(t))}removeController(t){var e;null===(e=this._$ES)||void 0===e||e.splice(this._$ES.indexOf(t)>>>0,1)}_$Eg(){this.constructor.elementProperties.forEach(((t,e)=>{this.hasOwnProperty(e)&&(this._$Ei.set(e,this[e]),delete this[e])}))}createRenderRoot(){var t;const e=null!==(t=this.shadowRoot)&&void 0!==t?t:this.attachShadow(this.constructor.shadowRootOptions);return((t,e)=>{at?t.adoptedStyleSheets=e.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet)):e.forEach((e=>{const i=document.createElement("style"),o=nt.litNonce;void 0!==o&&i.setAttribute("nonce",o),i.textContent=e.cssText,t.appendChild(i)}))})(e,this.constructor.elementStyles),e}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$ES)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)}))}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$ES)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)}))}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$EO(t,e,i=yt){var o;const s=this.constructor._$Ep(t,i);if(void 0!==s&&!0===i.reflect){const r=(void 0!==(null===(o=i.converter)||void 0===o?void 0:o.toAttribute)?i.converter:mt).toAttribute(e,i.type);this._$El=t,null==r?this.removeAttribute(s):this.setAttribute(s,r),this._$El=null}}_$AK(t,e){var i;const o=this.constructor,s=o._$Ev.get(t);if(void 0!==s&&this._$El!==s){const t=o.getPropertyOptions(s),r="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==(null===(i=t.converter)||void 0===i?void 0:i.fromAttribute)?t.converter:mt;this._$El=s,this[s]=r.fromAttribute(e,t.type),this._$El=null}}requestUpdate(t,e,i){let o=!0;void 0!==t&&(((i=i||this.constructor.getPropertyOptions(t)).hasChanged||gt)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===i.reflect&&this._$El!==t&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(t,i))):o=!1),!this.isUpdatePending&&o&&(this._$E_=this._$Ej())}async _$Ej(){this.isUpdatePending=!0;try{await this._$E_}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Ei&&(this._$Ei.forEach(((t,e)=>this[e]=t)),this._$Ei=void 0);let e=!1;const i=this._$AL;try{e=this.shouldUpdate(i),e?(this.willUpdate(i),null===(t=this._$ES)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)})),this.update(i)):this._$Ek()}catch(t){throw e=!1,this._$Ek(),t}e&&this._$AE(i)}willUpdate(t){}_$AE(t){var e;null===(e=this._$ES)||void 0===e||e.forEach((t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$Ek(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$E_}shouldUpdate(t){return!0}update(t){void 0!==this._$EC&&(this._$EC.forEach(((t,e)=>this._$EO(e,this[e],t))),this._$EC=void 0),this._$Ek()}updated(t){}firstUpdated(t){}};wt.finalized=!0,wt.elementProperties=new Map,wt.elementStyles=[],wt.shadowRootOptions={mode:"open"},null==vt||vt({ReactiveElement:wt}),(null!==(st=pt.reactiveElementVersions)&&void 0!==st?st:pt.reactiveElementVersions=[]).push("1.4.2");var _t=window,$t=_t.trustedTypes,xt=$t?$t.createPolicy("lit-html",{createHTML:t=>t}):void 0,kt=`lit$${(Math.random()+"").slice(9)}$`,At="?"+kt,Ct=`<${At}>`,Et=document,St=(t="")=>Et.createComment(t),Tt=t=>null===t||"object"!=typeof t&&"function"!=typeof t,zt=Array.isArray,Pt=t=>zt(t)||"function"==typeof(null==t?void 0:t[Symbol.iterator]),Lt=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,It=/-->/g,Ot=/>/g,Dt=RegExp(">|[ \t\n\f\r](?:([^\\s\"'>=/]+)([ \t\n\f\r]*=[ \t\n\f\r]*(?:[^ \t\n\f\r\"'`<>=]|(\"|')|))|$)","g"),Rt=/'/g,Ut=/"/g,Ft=/^(?:script|style|textarea|title)$/i,Bt=t=>(e,...i)=>({_$litType$:t,strings:e,values:i}),Ht=Bt(1),Mt=Bt(2),Nt=Symbol.for("lit-noChange"),Vt=Symbol.for("lit-nothing"),jt=new WeakMap,qt=Et.createTreeWalker(Et,129,null,!1),Wt=(t,e)=>{const i=t.length-1,o=[];let s,r=2===e?"<svg>":"",n=Lt;for(let e=0;e<i;e++){const i=t[e];let a,l,d=-1,c=0;for(;c<i.length&&(n.lastIndex=c,l=n.exec(i),null!==l);)c=n.lastIndex,n===Lt?"!--"===l[1]?n=It:void 0!==l[1]?n=Ot:void 0!==l[2]?(Ft.test(l[2])&&(s=RegExp("</"+l[2],"g")),n=Dt):void 0!==l[3]&&(n=Dt):n===Dt?">"===l[0]?(n=null!=s?s:Lt,d=-1):void 0===l[1]?d=-2:(d=n.lastIndex-l[2].length,a=l[1],n=void 0===l[3]?Dt:'"'===l[3]?Ut:Rt):n===Ut||n===Rt?n=Dt:n===It||n===Ot?n=Lt:(n=Dt,s=void 0);const h=n===Dt&&t[e+1].startsWith("/>")?" ":"";r+=n===Lt?i+Ct:d>=0?(o.push(a),i.slice(0,d)+"$lit$"+i.slice(d)+kt+h):i+kt+(-2===d?(o.push(void 0),e):h)}const a=r+(t[i]||"<?>")+(2===e?"</svg>":"");if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return[void 0!==xt?xt.createHTML(a):a,o]},Kt=class{constructor({strings:t,_$litType$:e},i){let o;this.parts=[];let s=0,r=0;const n=t.length-1,a=this.parts,[l,d]=Wt(t,e);if(this.el=Kt.createElement(l,i),qt.currentNode=this.el.content,2===e){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(o=qt.nextNode())&&a.length<n;){if(1===o.nodeType){if(o.hasAttributes()){const t=[];for(const e of o.getAttributeNames())if(e.endsWith("$lit$")||e.startsWith(kt)){const i=d[r++];if(t.push(e),void 0!==i){const t=o.getAttribute(i.toLowerCase()+"$lit$").split(kt),e=/([.?@])?(.*)/.exec(i);a.push({type:1,index:s,name:e[2],strings:t,ctor:"."===e[1]?Jt:"?"===e[1]?te:"@"===e[1]?ee:Xt})}else a.push({type:6,index:s})}for(const e of t)o.removeAttribute(e)}if(Ft.test(o.tagName)){const t=o.textContent.split(kt),e=t.length-1;if(e>0){o.textContent=$t?$t.emptyScript:"";for(let i=0;i<e;i++)o.append(t[i],St()),qt.nextNode(),a.push({type:2,index:++s});o.append(t[e],St())}}}else if(8===o.nodeType)if(o.data===At)a.push({type:2,index:s});else{let t=-1;for(;-1!==(t=o.data.indexOf(kt,t+1));)a.push({type:7,index:s}),t+=kt.length-1}s++}}static createElement(t,e){const i=Et.createElement("template");return i.innerHTML=t,i}};function Yt(t,e,i=t,o){var s,r,n,a;if(e===Nt)return e;let l=void 0!==o?null===(s=i._$Co)||void 0===s?void 0:s[o]:i._$Cl;const d=Tt(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==d&&(null===(r=null==l?void 0:l._$AO)||void 0===r||r.call(l,!1),void 0===d?l=void 0:(l=new d(t),l._$AT(t,i,o)),void 0!==o?(null!==(n=(a=i)._$Co)&&void 0!==n?n:a._$Co=[])[o]=l:i._$Cl=l),void 0!==l&&(e=Yt(t,l._$AS(t,e.values),l,o)),e}var Gt=class{constructor(t,e){this.u=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}v(t){var e;const{el:{content:i},parts:o}=this._$AD,s=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:Et).importNode(i,!0);qt.currentNode=s;let r=qt.nextNode(),n=0,a=0,l=o[0];for(;void 0!==l;){if(n===l.index){let e;2===l.type?e=new Zt(r,r.nextSibling,this,t):1===l.type?e=new l.ctor(r,l.name,l.strings,this,t):6===l.type&&(e=new ie(r,this,t)),this.u.push(e),l=o[++a]}n!==(null==l?void 0:l.index)&&(r=qt.nextNode(),n++)}return s}p(t){let e=0;for(const i of this.u)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}},Zt=class{constructor(t,e,i,o){var s;this.type=2,this._$AH=Vt,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=o,this._$Cm=null===(s=null==o?void 0:o.isConnected)||void 0===s||s}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cm}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=Yt(this,t,e),Tt(t)?t===Vt||null==t||""===t?(this._$AH!==Vt&&this._$AR(),this._$AH=Vt):t!==this._$AH&&t!==Nt&&this.g(t):void 0!==t._$litType$?this.$(t):void 0!==t.nodeType?this.T(t):Pt(t)?this.k(t):this.g(t)}O(t,e=this._$AB){return this._$AA.parentNode.insertBefore(t,e)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}g(t){this._$AH!==Vt&&Tt(this._$AH)?this._$AA.nextSibling.data=t:this.T(Et.createTextNode(t)),this._$AH=t}$(t){var e;const{values:i,_$litType$:o}=t,s="number"==typeof o?this._$AC(t):(void 0===o.el&&(o.el=Kt.createElement(o.h,this.options)),o);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===s)this._$AH.p(i);else{const t=new Gt(s,this),e=t.v(this.options);t.p(i),this.T(e),this._$AH=t}}_$AC(t){let e=jt.get(t.strings);return void 0===e&&jt.set(t.strings,e=new Kt(t)),e}k(t){zt(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let i,o=0;for(const s of t)o===e.length?e.push(i=new Zt(this.O(St()),this.O(St()),this,this.options)):i=e[o],i._$AI(s),o++;o<e.length&&(this._$AR(i&&i._$AB.nextSibling,o),e.length=o)}_$AR(t=this._$AA.nextSibling,e){var i;for(null===(i=this._$AP)||void 0===i||i.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cm=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}},Xt=class{constructor(t,e,i,o,s){this.type=1,this._$AH=Vt,this._$AN=void 0,this.element=t,this.name=e,this._$AM=o,this.options=s,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=Vt}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,i,o){const s=this.strings;let r=!1;if(void 0===s)t=Yt(this,t,e,0),r=!Tt(t)||t!==this._$AH&&t!==Nt,r&&(this._$AH=t);else{const o=t;let n,a;for(t=s[0],n=0;n<s.length-1;n++)a=Yt(this,o[i+n],e,n),a===Nt&&(a=this._$AH[n]),r||(r=!Tt(a)||a!==this._$AH[n]),a===Vt?t=Vt:t!==Vt&&(t+=(null!=a?a:"")+s[n+1]),this._$AH[n]=a}r&&!o&&this.j(t)}j(t){t===Vt?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}},Jt=class extends Xt{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===Vt?void 0:t}},Qt=$t?$t.emptyScript:"",te=class extends Xt{constructor(){super(...arguments),this.type=4}j(t){t&&t!==Vt?this.element.setAttribute(this.name,Qt):this.element.removeAttribute(this.name)}},ee=class extends Xt{constructor(t,e,i,o,s){super(t,e,i,o,s),this.type=5}_$AI(t,e=this){var i;if((t=null!==(i=Yt(this,t,e,0))&&void 0!==i?i:Vt)===Nt)return;const o=this._$AH,s=t===Vt&&o!==Vt||t.capture!==o.capture||t.once!==o.once||t.passive!==o.passive,r=t!==Vt&&(o===Vt||s);s&&this.element.removeEventListener(this.name,this,o),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,i;"function"==typeof this._$AH?this._$AH.call(null!==(i=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==i?i:this.element,t):this._$AH.handleEvent(t)}},ie=class{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){Yt(this,t)}},oe={P:"$lit$",A:kt,M:At,C:1,L:Wt,R:Gt,D:Pt,V:Yt,I:Zt,H:Xt,N:te,U:ee,B:Jt,F:ie},se=_t.litHtmlPolyfillSupport;null==se||se(Kt,Zt),(null!==(rt=_t.litHtmlVersions)&&void 0!==rt?rt:_t.litHtmlVersions=[]).push("2.4.0");var re,ne,ae=class extends wt{constructor(){super(...arguments),this.renderOptions={host:this},this._$Dt=void 0}createRenderRoot(){var t,e;const i=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=i.firstChild),i}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Dt=((t,e,i)=>{var o,s;const r=null!==(o=null==i?void 0:i.renderBefore)&&void 0!==o?o:e;let n=r._$litPart$;if(void 0===n){const t=null!==(s=null==i?void 0:i.renderBefore)&&void 0!==s?s:null;r._$litPart$=n=new Zt(e.insertBefore(St(),t),t,void 0,null!=i?i:{})}return n._$AI(t),n})(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!1)}render(){return Nt}};ae.finalized=!0,ae._$litElement$=!0,null===(re=globalThis.litElementHydrateSupport)||void 0===re||re.call(globalThis,{LitElement:ae});var le=globalThis.litElementPolyfillSupport;null==le||le({LitElement:ae}),(null!==(ne=globalThis.litElementVersions)&&void 0!==ne?ne:globalThis.litElementVersions=[]).push("3.2.0");var de=ht`
  :host {
    box-sizing: border-box;
  }

  :host *,
  :host *::before,
  :host *::after {
    box-sizing: inherit;
  }

  [hidden] {
    display: none !important;
  }
`,ce=ht`
  ${de}

  :host {
    --color: var(--sl-panel-border-color);
    --width: var(--sl-panel-border-width);
    --spacing: var(--sl-spacing-medium);
  }

  :host(:not([vertical])) {
    display: block;
    border-top: solid var(--width) var(--color);
    margin: var(--spacing) 0;
  }

  :host([vertical]) {
    display: inline-block;
    height: 100%;
    border-left: solid var(--width) var(--color);
    margin: 0 var(--spacing);
  }
`,he=Object.defineProperty,ue=Object.defineProperties,pe=Object.getOwnPropertyDescriptor,be=Object.getOwnPropertyDescriptors,fe=Object.getOwnPropertySymbols,ve=Object.prototype.hasOwnProperty,me=Object.prototype.propertyIsEnumerable,ge=(t,e,i)=>e in t?he(t,e,{enumerable:!0,configurable:!0,writable:!0,value:i}):t[e]=i,ye=(t,e)=>{for(var i in e||(e={}))ve.call(e,i)&&ge(t,i,e[i]);if(fe)for(var i of fe(e))me.call(e,i)&&ge(t,i,e[i]);return t},we=(t,e)=>ue(t,be(e)),_e=(t,e)=>{var i={};for(var o in t)ve.call(t,o)&&e.indexOf(o)<0&&(i[o]=t[o]);if(null!=t&&fe)for(var o of fe(t))e.indexOf(o)<0&&me.call(t,o)&&(i[o]=t[o]);return i},$e=(t,e,i,o)=>{for(var s,r=o>1?void 0:o?pe(e,i):e,n=t.length-1;n>=0;n--)(s=t[n])&&(r=(o?s(e,i,r):s(r))||r);return o&&r&&he(e,i,r),r};function xe(t,e){const i=ye({waitUntilFirstUpdate:!1},e);return(e,o)=>{const{update:s}=e;if(t in e){const r=t;e.update=function(t){if(t.has(r)){const e=t.get(r),s=this[r];e!==s&&(i.waitUntilFirstUpdate&&!this.hasUpdated||this[o](e,s))}s.call(this,t)}}}}var ke=t=>e=>"function"==typeof e?((t,e)=>(customElements.define(t,e),e))(t,e):((t,e)=>{const{kind:i,elements:o}=e;return{kind:i,elements:o,finisher(e){customElements.define(t,e)}}})(t,e),Ae=(t,e)=>"method"===e.kind&&e.descriptor&&!("value"in e.descriptor)?we(ye({},e),{finisher(i){i.createProperty(e.key,t)}}):{kind:"field",key:Symbol(),placement:"own",descriptor:{},originalKey:e.key,initializer(){"function"==typeof e.initializer&&(this[e.key]=e.initializer.call(this))},finisher(i){i.createProperty(e.key,t)}};function Ce(t){return(e,i)=>void 0!==i?((t,e,i)=>{e.constructor.createProperty(i,t)})(t,e,i):Ae(t,e)}function Ee(t){return Ce(we(ye({},t),{state:!0}))}var Se;function Te(t,e){return(({finisher:t,descriptor:e})=>(i,o)=>{var s;if(void 0===o){const o=null!==(s=i.originalKey)&&void 0!==s?s:i.key,r=null!=e?{kind:"method",placement:"prototype",key:o,descriptor:e(i.key)}:we(ye({},i),{key:o});return null!=t&&(r.finisher=function(e){t(e,o)}),r}{const s=i.constructor;void 0!==e&&Object.defineProperty(i,o,e(o)),null==t||t(s,o)}})({descriptor:i=>{const o={get(){var e,i;return null!==(i=null===(e=this.renderRoot)||void 0===e?void 0:e.querySelector(t))&&void 0!==i?i:null},enumerable:!0,configurable:!0};if(e){const e="symbol"==typeof i?Symbol():"__"+i;o.get=function(){var i,o;return void 0===this[e]&&(this[e]=null!==(o=null===(i=this.renderRoot)||void 0===i?void 0:i.querySelector(t))&&void 0!==o?o:null),this[e]}}return o}})}null===(Se=window.HTMLSlotElement)||void 0===Se||Se.prototype.assignedElements;var ze=class extends ae{emit(t,e){const i=new CustomEvent(t,ye({bubbles:!0,cancelable:!1,composed:!0,detail:{}},e));return this.dispatchEvent(i),i}};$e([Ce()],ze.prototype,"dir",2),$e([Ce()],ze.prototype,"lang",2);var Pe=class extends ze{constructor(){super(...arguments),this.vertical=!1}connectedCallback(){super.connectedCallback(),this.setAttribute("role","separator")}handleVerticalChange(){this.setAttribute("aria-orientation",this.vertical?"vertical":"horizontal")}};function Le(t){const e=t.tagName.toLowerCase();return"-1"!==t.getAttribute("tabindex")&&!t.hasAttribute("disabled")&&(!t.hasAttribute("aria-disabled")||"false"===t.getAttribute("aria-disabled"))&&!("input"===e&&"radio"===t.getAttribute("type")&&!t.hasAttribute("checked"))&&null!==t.offsetParent&&"hidden"!==window.getComputedStyle(t).visibility&&(!("audio"!==e&&"video"!==e||!t.hasAttribute("controls"))||!!t.hasAttribute("tabindex")||!(!t.hasAttribute("contenteditable")||"false"===t.getAttribute("contenteditable"))||["button","input","select","textarea","a","audio","video","summary"].includes(e))}Pe.styles=ce,$e([Ce({type:Boolean,reflect:!0})],Pe.prototype,"vertical",2),$e([xe("vertical")],Pe.prototype,"handleVerticalChange",1),Pe=$e([ke("sl-divider")],Pe);var Ie=[],Oe=new Set;function De(t){Oe.add(t),document.body.classList.add("sl-scroll-lock")}function Re(t){Oe.delete(t),0===Oe.size&&document.body.classList.remove("sl-scroll-lock")}function Ue(t,e,i="vertical",o="smooth"){const s=function(t,e){return{top:Math.round(t.getBoundingClientRect().top-e.getBoundingClientRect().top),left:Math.round(t.getBoundingClientRect().left-e.getBoundingClientRect().left)}}(t,e),r=s.top+e.scrollTop,n=s.left+e.scrollLeft,a=e.scrollLeft,l=e.scrollLeft+e.offsetWidth,d=e.scrollTop,c=e.scrollTop+e.offsetHeight;"horizontal"!==i&&"both"!==i||(n<a?e.scrollTo({left:n,behavior:o}):n+t.clientWidth>l&&e.scrollTo({left:n-e.offsetWidth+t.clientWidth,behavior:o})),"vertical"!==i&&"both"!==i||(r<d?e.scrollTo({top:r,behavior:o}):r+t.clientHeight>c&&e.scrollTo({top:r-e.offsetHeight+t.clientHeight,behavior:o}))}var Fe=ht`
  ${de}

  :host {
    --width: 31rem;
    --header-spacing: var(--sl-spacing-large);
    --body-spacing: var(--sl-spacing-large);
    --footer-spacing: var(--sl-spacing-large);

    display: contents;
  }

  .dialog {
    display: flex;
    align-items: center;
    justify-content: center;
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    z-index: var(--sl-z-index-dialog);
  }

  .dialog__panel {
    display: flex;
    flex-direction: column;
    z-index: 2;
    width: var(--width);
    max-width: calc(100% - var(--sl-spacing-2x-large));
    max-height: calc(100% - var(--sl-spacing-2x-large));
    background-color: var(--sl-panel-background-color);
    border-radius: var(--sl-border-radius-medium);
    box-shadow: var(--sl-shadow-x-large);
  }

  .dialog__panel:focus {
    outline: none;
  }

  /* Ensure there's enough vertical padding for phones that don't update vh when chrome appears (e.g. iPhone) */
  @media screen and (max-width: 420px) {
    .dialog__panel {
      max-height: 80vh;
    }
  }

  .dialog--open .dialog__panel {
    display: flex;
    opacity: 1;
  }

  .dialog__header {
    flex: 0 0 auto;
    display: flex;
  }

  .dialog__title {
    flex: 1 1 auto;
    font: inherit;
    font-size: var(--sl-font-size-large);
    line-height: var(--sl-line-height-dense);
    padding: var(--header-spacing);
    margin: 0;
  }

  .dialog__header-actions {
    flex-shrink: 0;
    display: flex;
    flex-wrap: wrap;
    justify-content: end;
    gap: var(--sl-spacing-2x-small);
    padding: 0 var(--header-spacing);
  }

  .dialog__header-actions sl-icon-button,
  .dialog__header-actions ::slotted(sl-icon-button) {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    font-size: var(--sl-font-size-medium);
  }

  .dialog__body {
    flex: 1 1 auto;
    display: block;
    padding: var(--body-spacing);
    overflow: auto;
    -webkit-overflow-scrolling: touch;
  }

  .dialog__footer {
    flex: 0 0 auto;
    text-align: right;
    padding: var(--footer-spacing);
  }

  .dialog__footer ::slotted(sl-button:not(:first-of-type)) {
    margin-inline-start: var(--sl-spacing-x-small);
  }

  .dialog:not(.dialog--has-footer) .dialog__footer {
    display: none;
  }

  .dialog__overlay {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    background-color: var(--sl-overlay-background-color);
  }

  @media (forced-colors: active) {
    .dialog__panel {
      border: solid 1px var(--sl-color-neutral-0);
    }
  }
`;function Be(t,e){return new Promise((i=>{t.addEventListener(e,(function o(s){s.target===t&&(t.removeEventListener(e,o),i())}))}))}function He(t,e,i){return new Promise((o=>{if((null==i?void 0:i.duration)===1/0)throw new Error("Promise-based animations must be finite.");const s=t.animate(e,we(ye({},i),{duration:window.matchMedia("(prefers-reduced-motion: reduce)").matches?0:i.duration}));s.addEventListener("cancel",o,{once:!0}),s.addEventListener("finish",o,{once:!0})}))}function Me(t){return(t=t.toString().toLowerCase()).indexOf("ms")>-1?parseFloat(t):t.indexOf("s")>-1?1e3*parseFloat(t):parseFloat(t)}function Ne(t){return Promise.all(t.getAnimations().map((t=>new Promise((e=>{const i=requestAnimationFrame(e);t.addEventListener("cancel",(()=>i),{once:!0}),t.addEventListener("finish",(()=>i),{once:!0}),t.cancel()})))))}function Ve(t,e){return t.map((t=>we(ye({},t),{height:"auto"===t.height?`${e}px`:t.height})))}var je=new Map,qe=new WeakMap;function We(t,e){return"rtl"===e.toLowerCase()?{keyframes:t.rtlKeyframes||t.keyframes,options:t.options}:t}function Ke(t,e){je.set(t,function(t){return null!=t?t:{keyframes:[],options:{duration:0}}}(e))}function Ye(t,e,i){const o=qe.get(t);if(null==o?void 0:o[e])return We(o[e],i.dir);const s=je.get(e);return s?We(s,i.dir):{keyframes:[],options:{duration:0}}}var Ge,Ze=new Set,Xe=new MutationObserver(ei),Je=new Map,Qe=document.documentElement.dir||"ltr",ti=document.documentElement.lang||navigator.language;function ei(){Qe=document.documentElement.dir||"ltr",ti=document.documentElement.lang||navigator.language,[...Ze.keys()].map((t=>{"function"==typeof t.requestUpdate&&t.requestUpdate()}))}Xe.observe(document.documentElement,{attributes:!0,attributeFilter:["dir","lang"]});var ii=class{constructor(t){this.host=t,this.host.addController(this)}hostConnected(){Ze.add(this.host)}hostDisconnected(){Ze.delete(this.host)}dir(){return`${this.host.dir||Qe}`.toLowerCase()}lang(){return`${this.host.lang||ti}`.toLowerCase()}term(t,...e){var i,o;const s=new Intl.Locale(this.lang()),r=null==s?void 0:s.language.toLowerCase(),n=null!==(o=null===(i=null==s?void 0:s.region)||void 0===i?void 0:i.toLowerCase())&&void 0!==o?o:"",a=Je.get(`${r}-${n}`),l=Je.get(r);let d;if(a&&a[t])d=a[t];else if(l&&l[t])d=l[t];else{if(!Ge||!Ge[t])return console.error(`No translation found for: ${String(t)}`),String(t);d=Ge[t]}return"function"==typeof d?d(...e):d}date(t,e){return t=new Date(t),new Intl.DateTimeFormat(this.lang(),e).format(t)}number(t,e){return t=Number(t),isNaN(t)?"":new Intl.NumberFormat(this.lang(),e).format(t)}relativeTime(t,e,i){return new Intl.RelativeTimeFormat(this.lang(),i).format(t,e)}},oi=class extends ii{};!function(...t){t.map((t=>{const e=t.$code.toLowerCase();Je.has(e)?Je.set(e,Object.assign(Object.assign({},Je.get(e)),t)):Je.set(e,t),Ge||(Ge=t)})),ei()}({$code:"en",$name:"English",$dir:"ltr",clearEntry:"Clear entry",close:"Close",copy:"Copy",numOptionsSelected:t=>0===t?"No options selected":1===t?"1 option selected":`${t} options selected`,currentValue:"Current value",hidePassword:"Hide password",loading:"Loading",progress:"Progress",remove:"Remove",resize:"Resize",scrollToEnd:"Scroll to end",scrollToStart:"Scroll to start",selectAColorFromTheScreen:"Select a color from the screen",showPassword:"Show password",toggleColorFormat:"Toggle color format"});var si=class{constructor(t,...e){this.slotNames=[],(this.host=t).addController(this),this.slotNames=e,this.handleSlotChange=this.handleSlotChange.bind(this)}hasDefaultSlot(){return[...this.host.childNodes].some((t=>{if(t.nodeType===t.TEXT_NODE&&""!==t.textContent.trim())return!0;if(t.nodeType===t.ELEMENT_NODE){const e=t;if("sl-visually-hidden"===e.tagName.toLowerCase())return!1;if(!e.hasAttribute("slot"))return!0}return!1}))}hasNamedSlot(t){return null!==this.host.querySelector(`:scope > [slot="${t}"]`)}test(t){return"[default]"===t?this.hasDefaultSlot():this.hasNamedSlot(t)}hostConnected(){this.host.shadowRoot.addEventListener("slotchange",this.handleSlotChange)}hostDisconnected(){this.host.shadowRoot.removeEventListener("slotchange",this.handleSlotChange)}handleSlotChange(t){const e=t.target;(this.slotNames.includes("[default]")&&!e.name||e.name&&this.slotNames.includes(e.name))&&this.host.requestUpdate()}},ri=t=>null!=t?t:Vt,ni=t=>(...e)=>({_$litDirective$:t,values:e}),ai=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,i){this._$Ct=t,this._$AM=e,this._$Ci=i}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}},li=ni(class extends ai{constructor(t){var e;if(super(t),1!==t.type||"class"!==t.name||(null===(e=t.strings)||void 0===e?void 0:e.length)>2)throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(t){return" "+Object.keys(t).filter((e=>t[e])).join(" ")+" "}update(t,[e]){var i,o;if(void 0===this.nt){this.nt=new Set,void 0!==t.strings&&(this.st=new Set(t.strings.join(" ").split(/\s/).filter((t=>""!==t))));for(const t in e)e[t]&&!(null===(i=this.st)||void 0===i?void 0:i.has(t))&&this.nt.add(t);return this.render(e)}const s=t.element.classList;this.nt.forEach((t=>{t in e||(s.remove(t),this.nt.delete(t))}));for(const t in e){const i=!!e[t];i===this.nt.has(t)||(null===(o=this.st)||void 0===o?void 0:o.has(t))||(i?(s.add(t),this.nt.add(t)):(s.remove(t),this.nt.delete(t)))}return Nt}}),di=class extends ze{constructor(){super(...arguments),this.hasSlotController=new si(this,"footer"),this.localize=new oi(this),this.open=!1,this.label="",this.noHeader=!1}connectedCallback(){super.connectedCallback(),this.handleDocumentKeyDown=this.handleDocumentKeyDown.bind(this),this.modal=new class{constructor(t){this.tabDirection="forward",this.element=t,this.handleFocusIn=this.handleFocusIn.bind(this),this.handleKeyDown=this.handleKeyDown.bind(this),this.handleKeyUp=this.handleKeyUp.bind(this)}activate(){Ie.push(this.element),document.addEventListener("focusin",this.handleFocusIn),document.addEventListener("keydown",this.handleKeyDown),document.addEventListener("keyup",this.handleKeyUp)}deactivate(){Ie=Ie.filter((t=>t!==this.element)),document.removeEventListener("focusin",this.handleFocusIn),document.removeEventListener("keydown",this.handleKeyDown),document.removeEventListener("keyup",this.handleKeyUp)}isActive(){return Ie[Ie.length-1]===this.element}checkFocus(){if(this.isActive()&&!this.element.matches(":focus-within")){const{start:t,end:e}=function(t){var e,i;const o=[];return function t(e){e instanceof HTMLElement&&(o.push(e),null!==e.shadowRoot&&"open"===e.shadowRoot.mode&&t(e.shadowRoot)),[...e.children].forEach((e=>t(e)))}(t),{start:null!=(e=o.find((t=>Le(t))))?e:null,end:null!=(i=o.reverse().find((t=>Le(t))))?i:null}}(this.element),i="forward"===this.tabDirection?t:e;"function"==typeof(null==i?void 0:i.focus)&&i.focus({preventScroll:!0})}}handleFocusIn(){this.checkFocus()}handleKeyDown(t){"Tab"===t.key&&t.shiftKey&&(this.tabDirection="backward",requestAnimationFrame((()=>this.checkFocus())))}handleKeyUp(){this.tabDirection="forward"}}(this)}firstUpdated(){this.dialog.hidden=!this.open,this.open&&(this.addOpenListeners(),this.modal.activate(),De(this))}disconnectedCallback(){super.disconnectedCallback(),Re(this)}requestClose(t){if(this.emit("sl-request-close",{cancelable:!0,detail:{source:t}}).defaultPrevented){const t=Ye(this,"dialog.denyClose",{dir:this.localize.dir()});He(this.panel,t.keyframes,t.options)}else this.hide()}addOpenListeners(){document.addEventListener("keydown",this.handleDocumentKeyDown)}removeOpenListeners(){document.removeEventListener("keydown",this.handleDocumentKeyDown)}handleDocumentKeyDown(t){this.open&&"Escape"===t.key&&(t.stopPropagation(),this.requestClose("keyboard"))}async handleOpenChange(){if(this.open){this.emit("sl-show"),this.addOpenListeners(),this.originalTrigger=document.activeElement,this.modal.activate(),De(this);const t=this.querySelector("[autofocus]");t&&t.removeAttribute("autofocus"),await Promise.all([Ne(this.dialog),Ne(this.overlay)]),this.dialog.hidden=!1,requestAnimationFrame((()=>{this.emit("sl-initial-focus",{cancelable:!0}).defaultPrevented||(t?t.focus({preventScroll:!0}):this.panel.focus({preventScroll:!0})),t&&t.setAttribute("autofocus","")}));const e=Ye(this,"dialog.show",{dir:this.localize.dir()}),i=Ye(this,"dialog.overlay.show",{dir:this.localize.dir()});await Promise.all([He(this.panel,e.keyframes,e.options),He(this.overlay,i.keyframes,i.options)]),this.emit("sl-after-show")}else{this.emit("sl-hide"),this.removeOpenListeners(),this.modal.deactivate(),await Promise.all([Ne(this.dialog),Ne(this.overlay)]);const t=Ye(this,"dialog.hide",{dir:this.localize.dir()}),e=Ye(this,"dialog.overlay.hide",{dir:this.localize.dir()});await Promise.all([He(this.overlay,e.keyframes,e.options).then((()=>{this.overlay.hidden=!0})),He(this.panel,t.keyframes,t.options).then((()=>{this.panel.hidden=!0}))]),this.dialog.hidden=!0,this.overlay.hidden=!1,this.panel.hidden=!1,Re(this);const i=this.originalTrigger;"function"==typeof(null==i?void 0:i.focus)&&setTimeout((()=>i.focus())),this.emit("sl-after-hide")}}async show(){if(!this.open)return this.open=!0,Be(this,"sl-after-show")}async hide(){if(this.open)return this.open=!1,Be(this,"sl-after-hide")}render(){return Ht`
      <div
        part="base"
        class=${li({dialog:!0,"dialog--open":this.open,"dialog--has-footer":this.hasSlotController.test("footer")})}
      >
        <div part="overlay" class="dialog__overlay" @click=${()=>this.requestClose("overlay")} tabindex="-1"></div>

        <div
          part="panel"
          class="dialog__panel"
          role="dialog"
          aria-modal="true"
          aria-hidden=${this.open?"false":"true"}
          aria-label=${ri(this.noHeader?this.label:void 0)}
          aria-labelledby=${ri(this.noHeader?void 0:"title")}
          tabindex="0"
        >
          ${this.noHeader?"":Ht`
                <header part="header" class="dialog__header">
                  <h2 part="title" class="dialog__title" id="title">
                    <slot name="label"> ${this.label.length>0?this.label:String.fromCharCode(65279)} </slot>
                  </h2>
                  <div part="header-actions" class="dialog__header-actions">
                    <slot name="header-actions"></slot>
                    <sl-icon-button
                      part="close-button"
                      exportparts="base:close-button__base"
                      class="dialog__close"
                      name="x-lg"
                      label=${this.localize.term("close")}
                      library="system"
                      @click="${()=>this.requestClose("close-button")}"
                    ></sl-icon-button>
                  </div>
                </header>
              `}

          <slot part="body" class="dialog__body"></slot>

          <footer part="footer" class="dialog__footer">
            <slot name="footer"></slot>
          </footer>
        </div>
      </div>
    `}};di.styles=Fe,$e([Te(".dialog")],di.prototype,"dialog",2),$e([Te(".dialog__panel")],di.prototype,"panel",2),$e([Te(".dialog__overlay")],di.prototype,"overlay",2),$e([Ce({type:Boolean,reflect:!0})],di.prototype,"open",2),$e([Ce({reflect:!0})],di.prototype,"label",2),$e([Ce({attribute:"no-header",type:Boolean,reflect:!0})],di.prototype,"noHeader",2),$e([xe("open",{waitUntilFirstUpdate:!0})],di.prototype,"handleOpenChange",1),di=$e([ke("sl-dialog")],di),Ke("dialog.show",{keyframes:[{opacity:0,scale:.8},{opacity:1,scale:1}],options:{duration:250,easing:"ease"}}),Ke("dialog.hide",{keyframes:[{opacity:1,scale:1},{opacity:0,scale:.8}],options:{duration:250,easing:"ease"}}),Ke("dialog.denyClose",{keyframes:[{scale:1},{scale:1.02},{scale:1}],options:{duration:250}}),Ke("dialog.overlay.show",{keyframes:[{opacity:0},{opacity:1}],options:{duration:250}}),Ke("dialog.overlay.hide",{keyframes:[{opacity:1},{opacity:0}],options:{duration:250}});var ci=ht`
  ${de}

  :host {
    display: inline-block;
    color: var(--sl-color-neutral-600);
  }

  .icon-button {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    background: none;
    border: none;
    border-radius: var(--sl-border-radius-medium);
    font-size: inherit;
    color: inherit;
    padding: var(--sl-spacing-x-small);
    cursor: pointer;
    transition: var(--sl-transition-x-fast) color;
    -webkit-appearance: none;
  }

  .icon-button:hover:not(.icon-button--disabled),
  .icon-button:focus-visible:not(.icon-button--disabled) {
    color: var(--sl-color-primary-600);
  }

  .icon-button:active:not(.icon-button--disabled) {
    color: var(--sl-color-primary-700);
  }

  .icon-button:focus {
    outline: none;
  }

  .icon-button--disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .icon-button:focus-visible {
    outline: var(--sl-focus-ring);
    outline-offset: var(--sl-focus-ring-offset);
  }

  .icon-button__icon {
    pointer-events: none;
  }
`,hi=Symbol.for(""),ui=t=>{if((null==t?void 0:t.r)===hi)return null==t?void 0:t._$litStatic$},pi=(t,...e)=>({_$litStatic$:e.reduce(((e,i,o)=>e+(t=>{if(void 0!==t._$litStatic$)return t._$litStatic$;throw Error(`Value passed to 'literal' function must be a 'literal' result: ${t}. Use 'unsafeStatic' to pass non-literal values, but\n            take care to ensure page security.`)})(i)+t[o+1]),t[0]),r:hi}),bi=new Map,fi=t=>(e,...i)=>{const o=i.length;let s,r;const n=[],a=[];let l,d=0,c=!1;for(;d<o;){for(l=e[d];d<o&&void 0!==(r=i[d],s=ui(r));)l+=s+e[++d],c=!0;a.push(r),n.push(l),d++}if(d===o&&n.push(e[o]),c){const t=n.join("$$lit$$");void 0===(e=bi.get(t))&&(n.raw=n,bi.set(t,e=n)),i=a}return t(e,...i)},vi=fi(Ht),mi=(fi(Mt),class extends ze{constructor(){super(...arguments),this.hasFocus=!1,this.label="",this.disabled=!1}handleBlur(){this.hasFocus=!1,this.emit("sl-blur")}handleFocus(){this.hasFocus=!0,this.emit("sl-focus")}handleClick(t){this.disabled&&(t.preventDefault(),t.stopPropagation())}click(){this.button.click()}focus(t){this.button.focus(t)}blur(){this.button.blur()}render(){const t=!!this.href,e=t?pi`a`:pi`button`;return vi`
      <${e}
        part="base"
        class=${li({"icon-button":!0,"icon-button--disabled":!t&&this.disabled,"icon-button--focused":this.hasFocus})}
        ?disabled=${ri(t?void 0:this.disabled)}
        type=${ri(t?void 0:"button")}
        href=${ri(t?this.href:void 0)}
        target=${ri(t?this.target:void 0)}
        download=${ri(t?this.download:void 0)}
        rel=${ri(t&&this.target?"noreferrer noopener":void 0)}
        role=${ri(t?void 0:"button")}
        aria-disabled=${this.disabled?"true":"false"}
        aria-label="${this.label}"
        tabindex=${this.disabled?"-1":"0"}
        @blur=${this.handleBlur}
        @focus=${this.handleFocus}
        @click=${this.handleClick}
      >
        <sl-icon
          class="icon-button__icon"
          name=${ri(this.name)}
          library=${ri(this.library)}
          src=${ri(this.src)}
          aria-hidden="true"
        ></sl-icon>
      </${e}>
    `}});mi.styles=ci,$e([Te(".icon-button")],mi.prototype,"button",2),$e([Ee()],mi.prototype,"hasFocus",2),$e([Ce()],mi.prototype,"name",2),$e([Ce()],mi.prototype,"library",2),$e([Ce()],mi.prototype,"src",2),$e([Ce()],mi.prototype,"href",2),$e([Ce()],mi.prototype,"target",2),$e([Ce()],mi.prototype,"download",2),$e([Ce()],mi.prototype,"label",2),$e([Ce({type:Boolean,reflect:!0})],mi.prototype,"disabled",2),mi=$e([ke("sl-icon-button")],mi);var gi="";function yi(t){gi=t}var wi={name:"default",resolver:t=>`${function(){if(!gi){const t=[...document.getElementsByTagName("script")],e=t.find((t=>t.hasAttribute("data-shoelace")));if(e)yi(e.getAttribute("data-shoelace"));else{const e=t.find((t=>/shoelace(\.min)?\.js($|\?)/.test(t.src)));let i="";e&&(i=e.getAttribute("src")),yi(i.split("/").slice(0,-1).join("/"))}}return gi.replace(/\/$/,"")}()}/assets/icons/${t}.svg`},_i={caret:'\n    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">\n      <polyline points="6 9 12 15 18 9"></polyline>\n    </svg>\n  ',check:'\n    <svg part="checked-icon" class="checkbox__icon" viewBox="0 0 16 16">\n      <g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd" stroke-linecap="round">\n        <g stroke="currentColor" stroke-width="2">\n          <g transform="translate(3.428571, 3.428571)">\n            <path d="M0,5.71428571 L3.42857143,9.14285714"></path>\n            <path d="M9.14285714,0 L3.42857143,9.14285714"></path>\n          </g>\n        </g>\n      </g>\n    </svg>\n  ',"chevron-down":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-down" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',"chevron-left":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-left" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0z"/>\n    </svg>\n  ',"chevron-right":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-right" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',eye:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye" viewBox="0 0 16 16">\n      <path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8zM1.173 8a13.133 13.133 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.133 13.133 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5c-2.12 0-3.879-1.168-5.168-2.457A13.134 13.134 0 0 1 1.172 8z"/>\n      <path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0z"/>\n    </svg>\n  ',"eye-slash":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye-slash" viewBox="0 0 16 16">\n      <path d="M13.359 11.238C15.06 9.72 16 8 16 8s-3-5.5-8-5.5a7.028 7.028 0 0 0-2.79.588l.77.771A5.944 5.944 0 0 1 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.134 13.134 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755-.165.165-.337.328-.517.486l.708.709z"/>\n      <path d="M11.297 9.176a3.5 3.5 0 0 0-4.474-4.474l.823.823a2.5 2.5 0 0 1 2.829 2.829l.822.822zm-2.943 1.299.822.822a3.5 3.5 0 0 1-4.474-4.474l.823.823a2.5 2.5 0 0 0 2.829 2.829z"/>\n      <path d="M3.35 5.47c-.18.16-.353.322-.518.487A13.134 13.134 0 0 0 1.172 8l.195.288c.335.48.83 1.12 1.465 1.755C4.121 11.332 5.881 12.5 8 12.5c.716 0 1.39-.133 2.02-.36l.77.772A7.029 7.029 0 0 1 8 13.5C3 13.5 0 8 0 8s.939-1.721 2.641-3.238l.708.709zm10.296 8.884-12-12 .708-.708 12 12-.708.708z"/>\n    </svg>\n  ',eyedropper:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eyedropper" viewBox="0 0 16 16">\n      <path d="M13.354.646a1.207 1.207 0 0 0-1.708 0L8.5 3.793l-.646-.647a.5.5 0 1 0-.708.708L8.293 5l-7.147 7.146A.5.5 0 0 0 1 12.5v1.793l-.854.853a.5.5 0 1 0 .708.707L1.707 15H3.5a.5.5 0 0 0 .354-.146L11 7.707l1.146 1.147a.5.5 0 0 0 .708-.708l-.647-.646 3.147-3.146a1.207 1.207 0 0 0 0-1.708l-2-2zM2 12.707l7-7L10.293 7l-7 7H2v-1.293z"></path>\n    </svg>\n  ',"grip-vertical":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-grip-vertical" viewBox="0 0 16 16">\n      <path d="M7 2a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zM7 5a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zM7 8a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm-3 3a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm-3 3a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"></path>\n    </svg>\n  ',indeterminate:'\n    <svg part="indeterminate-icon" class="checkbox__icon" viewBox="0 0 16 16">\n      <g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd" stroke-linecap="round">\n        <g stroke="currentColor" stroke-width="2">\n          <g transform="translate(2.285714, 6.857143)">\n            <path d="M10.2857143,1.14285714 L1.14285714,1.14285714"></path>\n          </g>\n        </g>\n      </g>\n    </svg>\n  ',"person-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-fill" viewBox="0 0 16 16">\n      <path d="M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H3zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/>\n    </svg>\n  ',"play-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-play-fill" viewBox="0 0 16 16">\n      <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"></path>\n    </svg>\n  ',"pause-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pause-fill" viewBox="0 0 16 16">\n      <path d="M5.5 3.5A1.5 1.5 0 0 1 7 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5zm5 0A1.5 1.5 0 0 1 12 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5z"></path>\n    </svg>\n  ',radio:'\n    <svg part="checked-icon" class="radio__icon" viewBox="0 0 16 16">\n      <g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">\n        <g fill="currentColor">\n          <circle cx="8" cy="8" r="3.42857143"></circle>\n        </g>\n      </g>\n    </svg>\n  ',"star-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-star-fill" viewBox="0 0 16 16">\n      <path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/>\n    </svg>\n  ',"x-lg":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-lg" viewBox="0 0 16 16">\n      <path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8 2.146 2.854Z"/>\n    </svg>\n  ',"x-circle-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-circle-fill" viewBox="0 0 16 16">\n      <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"></path>\n    </svg>\n  '},$i=[wi,{name:"system",resolver:t=>t in _i?`data:image/svg+xml,${encodeURIComponent(_i[t])}`:""}],xi=[];function ki(t){return $i.find((e=>e.name===t))}var Ai=new Map,Ci=new Map;var Ei=ht`
  ${de}

  :host {
    display: inline-block;
    width: 1em;
    height: 1em;
    contain: strict;
    box-sizing: content-box !important;
  }

  svg {
    display: block;
    height: 100%;
    width: 100%;
  }
`,Si=class extends ai{constructor(t){if(super(t),this.it=Vt,2!==t.type)throw Error(this.constructor.directiveName+"() can only be used in child bindings")}render(t){if(t===Vt||null==t)return this._t=void 0,this.it=t;if(t===Nt)return t;if("string"!=typeof t)throw Error(this.constructor.directiveName+"() called with a non-string value");if(t===this.it)return this._t;this.it=t;const e=[t];return e.raw=e,this._t={_$litType$:this.constructor.resultType,strings:e,values:[]}}};Si.directiveName="unsafeHTML",Si.resultType=1,ni(Si);var Ti=class extends Si{};Ti.directiveName="unsafeSVG",Ti.resultType=2;var zi,Pi=ni(Ti),Li=class extends ze{constructor(){super(...arguments),this.svg="",this.label="",this.library="default"}connectedCallback(){super.connectedCallback(),xi.push(this)}firstUpdated(){this.setIcon()}disconnectedCallback(){var t;super.disconnectedCallback(),t=this,xi=xi.filter((e=>e!==t))}getUrl(){const t=ki(this.library);return this.name&&t?t.resolver(this.name):this.src}handleLabelChange(){"string"==typeof this.label&&this.label.length>0?(this.setAttribute("role","img"),this.setAttribute("aria-label",this.label),this.removeAttribute("aria-hidden")):(this.removeAttribute("role"),this.removeAttribute("aria-label"),this.setAttribute("aria-hidden","true"))}async setIcon(){var t;const e=ki(this.library),i=this.getUrl();if(zi||(zi=new DOMParser),i)try{const o=await async function(t){if(Ci.has(t))return Ci.get(t);const e=await function(t,e="cors"){if(Ai.has(t))return Ai.get(t);const i=fetch(t,{mode:e}).then((async t=>({ok:t.ok,status:t.status,html:await t.text()})));return Ai.set(t,i),i}(t),i={ok:e.ok,status:e.status,svg:null};if(e.ok){const t=document.createElement("div");t.innerHTML=e.html;const o=t.firstElementChild;i.svg="svg"===(null==o?void 0:o.tagName.toLowerCase())?o.outerHTML:""}return Ci.set(t,i),i}(i);if(i!==this.getUrl())return;if(o.ok){const i=zi.parseFromString(o.svg,"text/html").body.querySelector("svg");null!==i?(null==(t=null==e?void 0:e.mutator)||t.call(e,i),this.svg=i.outerHTML,this.emit("sl-load")):(this.svg="",this.emit("sl-error"))}else this.svg="",this.emit("sl-error")}catch(t){this.emit("sl-error")}else this.svg.length>0&&(this.svg="")}render(){return Ht` ${Pi(this.svg)} `}};Li.styles=Ei,$e([Ee()],Li.prototype,"svg",2),$e([Ce({reflect:!0})],Li.prototype,"name",2),$e([Ce()],Li.prototype,"src",2),$e([Ce()],Li.prototype,"label",2),$e([Ce({reflect:!0})],Li.prototype,"library",2),$e([xe("label")],Li.prototype,"handleLabelChange",1),$e([xe("name"),xe("src"),xe("library")],Li.prototype,"setIcon",1),Li=$e([ke("sl-icon")],Li);var Ii=ht`
  ${de}

  :host {
    --max-width: 20rem;
    --hide-delay: 0ms;
    --show-delay: 150ms;

    display: contents;
  }

  .tooltip {
    --arrow-size: var(--sl-tooltip-arrow-size);
    --arrow-color: var(--sl-tooltip-background-color);
  }

  .tooltip::part(popup) {
    pointer-events: none;
    z-index: var(--sl-z-index-tooltip);
  }

  .tooltip[placement^='top']::part(popup) {
    transform-origin: bottom;
  }

  .tooltip[placement^='bottom']::part(popup) {
    transform-origin: top;
  }

  .tooltip[placement^='left']::part(popup) {
    transform-origin: right;
  }

  .tooltip[placement^='right']::part(popup) {
    transform-origin: left;
  }

  .tooltip__body {
    display: block;
    width: max-content;
    max-width: var(--max-width);
    border-radius: var(--sl-tooltip-border-radius);
    background-color: var(--sl-tooltip-background-color);
    font-family: var(--sl-tooltip-font-family);
    font-size: var(--sl-tooltip-font-size);
    font-weight: var(--sl-tooltip-font-weight);
    line-height: var(--sl-tooltip-line-height);
    color: var(--sl-tooltip-color);
    padding: var(--sl-tooltip-padding);
    pointer-events: none;
  }
`,Oi=class extends ze{constructor(){super(...arguments),this.localize=new oi(this),this.content="",this.placement="top",this.disabled=!1,this.distance=8,this.open=!1,this.skidding=0,this.trigger="hover focus",this.hoist=!1}connectedCallback(){super.connectedCallback(),this.handleBlur=this.handleBlur.bind(this),this.handleClick=this.handleClick.bind(this),this.handleFocus=this.handleFocus.bind(this),this.handleKeyDown=this.handleKeyDown.bind(this),this.handleMouseOver=this.handleMouseOver.bind(this),this.handleMouseOut=this.handleMouseOut.bind(this),this.updateComplete.then((()=>{this.addEventListener("blur",this.handleBlur,!0),this.addEventListener("focus",this.handleFocus,!0),this.addEventListener("click",this.handleClick),this.addEventListener("keydown",this.handleKeyDown),this.addEventListener("mouseover",this.handleMouseOver),this.addEventListener("mouseout",this.handleMouseOut)}))}firstUpdated(){this.body.hidden=!this.open,this.open&&(this.popup.active=!0,this.popup.reposition())}disconnectedCallback(){super.disconnectedCallback(),this.removeEventListener("blur",this.handleBlur,!0),this.removeEventListener("focus",this.handleFocus,!0),this.removeEventListener("click",this.handleClick),this.removeEventListener("keydown",this.handleKeyDown),this.removeEventListener("mouseover",this.handleMouseOver),this.removeEventListener("mouseout",this.handleMouseOut)}handleBlur(){this.hasTrigger("focus")&&this.hide()}handleClick(){this.hasTrigger("click")&&(this.open?this.hide():this.show())}handleFocus(){this.hasTrigger("focus")&&this.show()}handleKeyDown(t){this.open&&"Escape"===t.key&&(t.stopPropagation(),this.hide())}handleMouseOver(){if(this.hasTrigger("hover")){const t=Me(getComputedStyle(this).getPropertyValue("--show-delay"));clearTimeout(this.hoverTimeout),this.hoverTimeout=window.setTimeout((()=>this.show()),t)}}handleMouseOut(){if(this.hasTrigger("hover")){const t=Me(getComputedStyle(this).getPropertyValue("--hide-delay"));clearTimeout(this.hoverTimeout),this.hoverTimeout=window.setTimeout((()=>this.hide()),t)}}hasTrigger(t){return this.trigger.split(" ").includes(t)}async handleOpenChange(){if(this.open){if(this.disabled)return;this.emit("sl-show"),await Ne(this.body),this.body.hidden=!1,this.popup.active=!0;const{keyframes:t,options:e}=Ye(this,"tooltip.show",{dir:this.localize.dir()});await He(this.popup.popup,t,e),this.emit("sl-after-show")}else{this.emit("sl-hide"),await Ne(this.body);const{keyframes:t,options:e}=Ye(this,"tooltip.hide",{dir:this.localize.dir()});await He(this.popup.popup,t,e),this.popup.active=!1,this.body.hidden=!0,this.emit("sl-after-hide")}}async handleOptionsChange(){this.hasUpdated&&(await this.updateComplete,this.popup.reposition())}handleDisabledChange(){this.disabled&&this.open&&this.hide()}async show(){if(!this.open)return this.open=!0,Be(this,"sl-after-show")}async hide(){if(this.open)return this.open=!1,Be(this,"sl-after-hide")}render(){return Ht`
      <sl-popup
        part="base"
        exportparts="
          popup:base__popup,
          arrow:base__arrow
        "
        class=${li({tooltip:!0,"tooltip--open":this.open})}
        placement=${this.placement}
        distance=${this.distance}
        skidding=${this.skidding}
        strategy=${this.hoist?"fixed":"absolute"}
        flip
        shift
        arrow
      >
        <slot slot="anchor" aria-describedby="tooltip"></slot>

        <slot
          name="content"
          part="body"
          id="tooltip"
          class="tooltip__body"
          role="tooltip"
          aria-live=${this.open?"polite":"off"}
        >
          ${this.content}
        </slot>
      </sl-popup>
    `}};Oi.styles=Ii,$e([Te("slot:not([name])")],Oi.prototype,"defaultSlot",2),$e([Te(".tooltip__body")],Oi.prototype,"body",2),$e([Te("sl-popup")],Oi.prototype,"popup",2),$e([Ce()],Oi.prototype,"content",2),$e([Ce()],Oi.prototype,"placement",2),$e([Ce({type:Boolean,reflect:!0})],Oi.prototype,"disabled",2),$e([Ce({type:Number})],Oi.prototype,"distance",2),$e([Ce({type:Boolean,reflect:!0})],Oi.prototype,"open",2),$e([Ce({type:Number})],Oi.prototype,"skidding",2),$e([Ce()],Oi.prototype,"trigger",2),$e([Ce({type:Boolean})],Oi.prototype,"hoist",2),$e([xe("open",{waitUntilFirstUpdate:!0})],Oi.prototype,"handleOpenChange",1),$e([xe("content"),xe("distance"),xe("hoist"),xe("placement"),xe("skidding")],Oi.prototype,"handleOptionsChange",1),$e([xe("disabled")],Oi.prototype,"handleDisabledChange",1),Oi=$e([ke("sl-tooltip")],Oi),Ke("tooltip.show",{keyframes:[{opacity:0,scale:.8},{opacity:1,scale:1}],options:{duration:150,easing:"ease"}}),Ke("tooltip.hide",{keyframes:[{opacity:1,scale:1},{opacity:0,scale:.8}],options:{duration:150,easing:"ease"}});var Di=ht`
  ${de}

  :host {
    --arrow-color: var(--sl-color-neutral-1000);
    --arrow-size: 6px;

    /*
     * These properties are computed to account for the arrow's dimensions after being rotated 45º. The constant
     * 0.7071 is derived from sin(45), which is the diagonal size of the arrow's container after rotating.
     */
    --arrow-size-diagonal: calc(var(--arrow-size) * 0.7071);
    --arrow-padding-offset: calc(var(--arrow-size-diagonal) - var(--arrow-size));

    display: contents;
  }

  .popup {
    position: absolute;
    isolation: isolate;
    max-width: var(--auto-size-available-width, none);
    max-height: var(--auto-size-available-height, none);
  }

  .popup--fixed {
    position: fixed;
  }

  .popup:not(.popup--active) {
    display: none;
  }

  .popup__arrow {
    position: absolute;
    width: calc(var(--arrow-size-diagonal) * 2);
    height: calc(var(--arrow-size-diagonal) * 2);
    rotate: 45deg;
    background: var(--arrow-color);
    z-index: -1;
  }
`;function Ri(t){return t.split("-")[0]}function Ui(t){return t.split("-")[1]}function Fi(t){return["top","bottom"].includes(Ri(t))?"x":"y"}function Bi(t){return"y"===t?"height":"width"}function Hi(t,e,i){let{reference:o,floating:s}=t;const r=o.x+o.width/2-s.width/2,n=o.y+o.height/2-s.height/2,a=Fi(e),l=Bi(a),d=o[l]/2-s[l]/2,c="x"===a;let h;switch(Ri(e)){case"top":h={x:r,y:o.y-s.height};break;case"bottom":h={x:r,y:o.y+o.height};break;case"right":h={x:o.x+o.width,y:n};break;case"left":h={x:o.x-s.width,y:n};break;default:h={x:o.x,y:o.y}}switch(Ui(e)){case"start":h[a]-=d*(i&&c?-1:1);break;case"end":h[a]+=d*(i&&c?-1:1)}return h}function Mi(t){return"number"!=typeof t?function(t){return ye({top:0,right:0,bottom:0,left:0},t)}(t):{top:t,right:t,bottom:t,left:t}}function Ni(t){return we(ye({},t),{top:t.y,left:t.x,right:t.x+t.width,bottom:t.y+t.height})}async function Vi(t,e){var i;void 0===e&&(e={});const{x:o,y:s,platform:r,rects:n,elements:a,strategy:l}=t,{boundary:d="clippingAncestors",rootBoundary:c="viewport",elementContext:h="floating",altBoundary:u=!1,padding:p=0}=e,b=Mi(p),f=a[u?"floating"===h?"reference":"floating":h],v=Ni(await r.getClippingRect({element:null==(i=await(null==r.isElement?void 0:r.isElement(f)))||i?f:f.contextElement||await(null==r.getDocumentElement?void 0:r.getDocumentElement(a.floating)),boundary:d,rootBoundary:c,strategy:l})),m=Ni(r.convertOffsetParentRelativeRectToViewportRelativeRect?await r.convertOffsetParentRelativeRectToViewportRelativeRect({rect:"floating"===h?we(ye({},n.floating),{x:o,y:s}):n.reference,offsetParent:await(null==r.getOffsetParent?void 0:r.getOffsetParent(a.floating)),strategy:l}):n[h]);return{top:v.top-m.top+b.top,bottom:m.bottom-v.bottom+b.bottom,left:v.left-m.left+b.left,right:m.right-v.right+b.right}}var ji=Math.min,qi=Math.max;function Wi(t,e,i){return qi(t,ji(e,i))}var Ki={left:"right",right:"left",bottom:"top",top:"bottom"};function Yi(t){return t.replace(/left|right|bottom|top/g,(t=>Ki[t]))}var Gi={start:"end",end:"start"};function Zi(t){return t.replace(/start|end/g,(t=>Gi[t]))}["top","right","bottom","left"].reduce(((t,e)=>t.concat(e,e+"-start",e+"-end")),[]);var Xi=function(t){return void 0===t&&(t=0),{name:"offset",options:t,async fn(e){const{x:i,y:o}=e,s=await async function(t,e){const{placement:i,platform:o,elements:s}=t,r=await(null==o.isRTL?void 0:o.isRTL(s.floating)),n=Ri(i),a=Ui(i),l="x"===Fi(i),d=["left","top"].includes(n)?-1:1,c=r&&l?-1:1,h="function"==typeof e?e(t):e;let{mainAxis:u,crossAxis:p,alignmentAxis:b}="number"==typeof h?{mainAxis:h,crossAxis:0,alignmentAxis:null}:ye({mainAxis:0,crossAxis:0,alignmentAxis:null},h);return a&&"number"==typeof b&&(p="end"===a?-1*b:b),l?{x:p*c,y:u*d}:{x:u*d,y:p*c}}(e,t);return{x:i+s.x,y:o+s.y,data:s}}}},Ji=function(t){return void 0===t&&(t={}),{name:"size",options:t,async fn(e){const{placement:i,rects:o,platform:s,elements:r}=e,n=t,{apply:a=(()=>{})}=n,l=_e(n,["apply"]),d=await Vi(e,l),c=Ri(i),h=Ui(i);let u,p;"top"===c||"bottom"===c?(u=c,p=h===(await(null==s.isRTL?void 0:s.isRTL(r.floating))?"start":"end")?"left":"right"):(p=c,u="end"===h?"top":"bottom");const b=qi(d.left,0),f=qi(d.right,0),v=qi(d.top,0),m=qi(d.bottom,0),g={availableHeight:o.floating.height-(["left","right"].includes(i)?2*(0!==v||0!==m?v+m:qi(d.top,d.bottom)):d[u]),availableWidth:o.floating.width-(["top","bottom"].includes(i)?2*(0!==b||0!==f?b+f:qi(d.left,d.right)):d[p])};await a(ye(ye({},e),g));const y=await s.getDimensions(r.floating);return o.floating.width!==y.width||o.floating.height!==y.height?{reset:{rects:!0}}:{}}}};function Qi(t){return t&&t.document&&t.location&&t.alert&&t.setInterval}function to(t){if(null==t)return window;if(!Qi(t)){const e=t.ownerDocument;return e&&e.defaultView||window}return t}function eo(t){return to(t).getComputedStyle(t)}function io(t){return Qi(t)?"":t?(t.nodeName||"").toLowerCase():""}function oo(){const t=navigator.userAgentData;return t&&Array.isArray(t.brands)?t.brands.map((t=>t.brand+"/"+t.version)).join(" "):navigator.userAgent}function so(t){return t instanceof to(t).HTMLElement}function ro(t){return t instanceof to(t).Element}function no(t){return"undefined"!=typeof ShadowRoot&&(t instanceof to(t).ShadowRoot||t instanceof ShadowRoot)}function ao(t){const{overflow:e,overflowX:i,overflowY:o,display:s}=eo(t);return/auto|scroll|overlay|hidden/.test(e+o+i)&&!["inline","contents"].includes(s)}function lo(t){return["table","td","th"].includes(io(t))}function co(t){const e=/firefox/i.test(oo()),i=eo(t),o=i.backdropFilter||i.WebkitBackdropFilter;return"none"!==i.transform||"none"!==i.perspective||!!o&&"none"!==o||e&&"filter"===i.willChange||e&&!!i.filter&&"none"!==i.filter||["transform","perspective"].some((t=>i.willChange.includes(t)))||["paint","layout","strict","content"].some((t=>{const e=i.contain;return null!=e&&e.includes(t)}))}function ho(){return!/^((?!chrome|android).)*safari/i.test(oo())}function uo(t){return["html","body","#document"].includes(io(t))}var po=Math.min,bo=Math.max,fo=Math.round;function vo(t,e,i){var o,s,r,n;void 0===e&&(e=!1),void 0===i&&(i=!1);const a=t.getBoundingClientRect();let l=1,d=1;e&&so(t)&&(l=t.offsetWidth>0&&fo(a.width)/t.offsetWidth||1,d=t.offsetHeight>0&&fo(a.height)/t.offsetHeight||1);const c=ro(t)?to(t):window,h=!ho()&&i,u=(a.left+(h&&null!=(o=null==(s=c.visualViewport)?void 0:s.offsetLeft)?o:0))/l,p=(a.top+(h&&null!=(r=null==(n=c.visualViewport)?void 0:n.offsetTop)?r:0))/d,b=a.width/l,f=a.height/d;return{width:b,height:f,top:p,right:u+b,bottom:p+f,left:u,x:u,y:p}}function mo(t){return(e=t,(e instanceof to(e).Node?t.ownerDocument:t.document)||window.document).documentElement;var e}function go(t){return ro(t)?{scrollLeft:t.scrollLeft,scrollTop:t.scrollTop}:{scrollLeft:t.pageXOffset,scrollTop:t.pageYOffset}}function yo(t){return vo(mo(t)).left+go(t).scrollLeft}function wo(t,e,i){const o=so(e),s=mo(e),r=vo(t,o&&function(t){const e=vo(t);return fo(e.width)!==t.offsetWidth||fo(e.height)!==t.offsetHeight}(e),"fixed"===i);let n={scrollLeft:0,scrollTop:0};const a={x:0,y:0};if(o||!o&&"fixed"!==i)if(("body"!==io(e)||ao(s))&&(n=go(e)),so(e)){const t=vo(e,!0);a.x=t.x+e.clientLeft,a.y=t.y+e.clientTop}else s&&(a.x=yo(s));return{x:r.left+n.scrollLeft-a.x,y:r.top+n.scrollTop-a.y,width:r.width,height:r.height}}function _o(t){if("html"===io(t))return t;const e=t.assignedSlot||t.parentNode||(no(t)?t.host:null)||mo(t);return no(e)?e.host:e}function $o(t){return so(t)&&"fixed"!==eo(t).position?t.offsetParent:null}function xo(t){const e=to(t);let i=$o(t);for(;i&&lo(i)&&"static"===eo(i).position;)i=$o(i);return i&&("html"===io(i)||"body"===io(i)&&"static"===eo(i).position&&!co(i))?e:i||function(t){let e=_o(t);for(;so(e)&&!uo(e);){if(co(e))return e;e=_o(e)}return null}(t)||e}function ko(t){const e=_o(t);return uo(e)?t.ownerDocument.body:so(e)&&ao(e)?e:ko(e)}function Ao(t,e){var i;void 0===e&&(e=[]);const o=ko(t),s=o===(null==(i=t.ownerDocument)?void 0:i.body),r=to(o),n=s?[r].concat(r.visualViewport||[],ao(o)?o:[]):o,a=e.concat(n);return s?a:a.concat(Ao(n))}function Co(t,e,i){return"viewport"===e?Ni(function(t,e){const i=to(t),o=mo(t),s=i.visualViewport;let r=o.clientWidth,n=o.clientHeight,a=0,l=0;if(s){r=s.width,n=s.height;const t=ho();(t||!t&&"fixed"===e)&&(a=s.offsetLeft,l=s.offsetTop)}return{width:r,height:n,x:a,y:l}}(t,i)):ro(e)?function(t,e){const i=vo(t,!1,"fixed"===e),o=i.top+t.clientTop,s=i.left+t.clientLeft;return{top:o,left:s,x:s,y:o,right:s+t.clientWidth,bottom:o+t.clientHeight,width:t.clientWidth,height:t.clientHeight}}(e,i):Ni(function(t){var e;const i=mo(t),o=go(t),s=null==(e=t.ownerDocument)?void 0:e.body,r=bo(i.scrollWidth,i.clientWidth,s?s.scrollWidth:0,s?s.clientWidth:0),n=bo(i.scrollHeight,i.clientHeight,s?s.scrollHeight:0,s?s.clientHeight:0);let a=-o.scrollLeft+yo(t);const l=-o.scrollTop;return"rtl"===eo(s||i).direction&&(a+=bo(i.clientWidth,s?s.clientWidth:0)-r),{width:r,height:n,x:a,y:l}}(mo(t)))}var Eo={getClippingRect:function(t){let{element:e,boundary:i,rootBoundary:o,strategy:s}=t;const r="clippingAncestors"===i?function(t){let e=Ao(t).filter((t=>ro(t)&&"body"!==io(t))),i=null;const o="fixed"===eo(t).position;let s=o?_o(t):t;for(;ro(s)&&!uo(s);){const t=eo(s),r=co(s);(o?r||i:r||"static"!==t.position||!i||!["absolute","fixed"].includes(i.position))?i=t:e=e.filter((t=>t!==s)),s=_o(s)}return e}(e):[].concat(i),n=[...r,o],a=n[0],l=n.reduce(((t,i)=>{const o=Co(e,i,s);return t.top=bo(o.top,t.top),t.right=po(o.right,t.right),t.bottom=po(o.bottom,t.bottom),t.left=bo(o.left,t.left),t}),Co(e,a,s));return{width:l.right-l.left,height:l.bottom-l.top,x:l.left,y:l.top}},convertOffsetParentRelativeRectToViewportRelativeRect:function(t){let{rect:e,offsetParent:i,strategy:o}=t;const s=so(i),r=mo(i);if(i===r)return e;let n={scrollLeft:0,scrollTop:0};const a={x:0,y:0};if((s||!s&&"fixed"!==o)&&(("body"!==io(i)||ao(r))&&(n=go(i)),so(i))){const t=vo(i,!0);a.x=t.x+i.clientLeft,a.y=t.y+i.clientTop}return we(ye({},e),{x:e.x-n.scrollLeft+a.x,y:e.y-n.scrollTop+a.y})},isElement:ro,getDimensions:function(t){if(so(t))return{width:t.offsetWidth,height:t.offsetHeight};const e=vo(t);return{width:e.width,height:e.height}},getOffsetParent:xo,getDocumentElement:mo,async getElementRects(t){let{reference:e,floating:i,strategy:o}=t;const s=this.getOffsetParent||xo,r=this.getDimensions;return{reference:wo(e,await s(i),o),floating:ye({x:0,y:0},await r(i))}},getClientRects:t=>Array.from(t.getClientRects()),isRTL:t=>"rtl"===eo(t).direction},So=class extends ze{constructor(){super(...arguments),this.active=!1,this.placement="top",this.strategy="absolute",this.distance=0,this.skidding=0,this.arrow=!1,this.arrowPlacement="anchor",this.arrowPadding=10,this.flip=!1,this.flipFallbackPlacements="",this.flipFallbackStrategy="best-fit",this.flipPadding=0,this.shift=!1,this.shiftPadding=0,this.autoSizePadding=0}async connectedCallback(){super.connectedCallback(),await this.updateComplete,this.start()}disconnectedCallback(){this.stop()}async updated(t){super.updated(t),t.has("active")&&(this.active?this.start():this.stop()),t.has("anchor")&&this.handleAnchorChange(),this.active&&(await this.updateComplete,this.reposition())}async handleAnchorChange(){if(await this.stop(),this.anchor&&"string"==typeof this.anchor){const t=this.getRootNode();this.anchorEl=t.getElementById(this.anchor)}else this.anchor instanceof HTMLElement?this.anchorEl=this.anchor:this.anchorEl=this.querySelector('[slot="anchor"]');if(this.anchorEl instanceof HTMLSlotElement&&(this.anchorEl=this.anchorEl.assignedElements({flatten:!0})[0]),!this.anchorEl)throw new Error("Invalid anchor element: no anchor could be found using the anchor slot or the anchor attribute.");this.start()}start(){this.anchorEl&&(this.cleanup=function(t,e,i,o){void 0===o&&(o={});const{ancestorScroll:s=!0,ancestorResize:r=!0,elementResize:n=!0,animationFrame:a=!1}=o,l=s&&!a,d=l||r?[...ro(t)?Ao(t):t.contextElement?Ao(t.contextElement):[],...Ao(e)]:[];d.forEach((t=>{l&&t.addEventListener("scroll",i,{passive:!0}),r&&t.addEventListener("resize",i)}));let c,h=null;if(n){let o=!0;h=new ResizeObserver((()=>{o||i(),o=!1})),ro(t)&&!a&&h.observe(t),ro(t)||!t.contextElement||a||h.observe(t.contextElement),h.observe(e)}let u=a?vo(t):null;return a&&function e(){const o=vo(t);!u||o.x===u.x&&o.y===u.y&&o.width===u.width&&o.height===u.height||i(),u=o,c=requestAnimationFrame(e)}(),i(),()=>{var t;d.forEach((t=>{l&&t.removeEventListener("scroll",i),r&&t.removeEventListener("resize",i)})),null==(t=h)||t.disconnect(),h=null,a&&cancelAnimationFrame(c)}}(this.anchorEl,this.popup,(()=>{this.reposition()})))}async stop(){return new Promise((t=>{this.cleanup?(this.cleanup(),this.cleanup=void 0,this.removeAttribute("data-current-placement"),this.style.removeProperty("--auto-size-available-width"),this.style.removeProperty("--auto-size-available-height"),requestAnimationFrame((()=>t()))):t()}))}reposition(){if(!this.active||!this.anchorEl)return;const t=[Xi({mainAxis:this.distance,crossAxis:this.skidding})];var e;this.sync?t.push(Ji({apply:({rects:t})=>{const e="width"===this.sync||"both"===this.sync,i="height"===this.sync||"both"===this.sync;this.popup.style.width=e?`${t.reference.width}px`:"",this.popup.style.height=i?`${t.reference.height}px`:""}})):(this.popup.style.width="",this.popup.style.height=""),this.flip&&t.push((void 0===(e={boundary:this.flipBoundary,fallbackPlacements:this.flipFallbackPlacements,fallbackStrategy:"best-fit"===this.flipFallbackStrategy?"bestFit":"initialPlacement",padding:this.flipPadding})&&(e={}),{name:"flip",options:e,async fn(t){var i;const{placement:o,middlewareData:s,rects:r,initialPlacement:n,platform:a,elements:l}=t,d=e,{mainAxis:c=!0,crossAxis:h=!0,fallbackPlacements:u,fallbackStrategy:p="bestFit",flipAlignment:b=!0}=d,f=_e(d,["mainAxis","crossAxis","fallbackPlacements","fallbackStrategy","flipAlignment"]),v=Ri(o),m=u||(v!==n&&b?function(t){const e=Yi(t);return[Zi(t),e,Zi(e)]}(n):[Yi(n)]),g=[n,...m],y=await Vi(t,f),w=[];let _=(null==(i=s.flip)?void 0:i.overflows)||[];if(c&&w.push(y[v]),h){const{main:t,cross:e}=function(t,e,i){void 0===i&&(i=!1);const o=Ui(t),s=Fi(t),r=Bi(s);let n="x"===s?o===(i?"end":"start")?"right":"left":"start"===o?"bottom":"top";return e.reference[r]>e.floating[r]&&(n=Yi(n)),{main:n,cross:Yi(n)}}(o,r,await(null==a.isRTL?void 0:a.isRTL(l.floating)));w.push(y[t],y[e])}if(_=[..._,{placement:o,overflows:w}],!w.every((t=>t<=0))){var $,x;const t=(null!=($=null==(x=s.flip)?void 0:x.index)?$:0)+1,e=g[t];if(e)return{data:{index:t,overflows:_},reset:{placement:e}};let i="bottom";switch(p){case"bestFit":{var k;const t=null==(k=_.map((t=>[t,t.overflows.filter((t=>t>0)).reduce(((t,e)=>t+e),0)])).sort(((t,e)=>t[1]-e[1]))[0])?void 0:k[0].placement;t&&(i=t);break}case"initialPlacement":i=n}if(o!==i)return{reset:{placement:i}}}return{}}})),this.shift&&t.push(function(t){return void 0===t&&(t={}),{name:"shift",options:t,async fn(e){const{x:i,y:o,placement:s}=e,r=t,{mainAxis:n=!0,crossAxis:a=!1,limiter:l={fn:t=>{let{x:e,y:i}=t;return{x:e,y:i}}}}=r,d=_e(r,["mainAxis","crossAxis","limiter"]),c={x:i,y:o},h=await Vi(e,d),u=Fi(Ri(s)),p=function(t){return"x"===t?"y":"x"}(u);let b=c[u],f=c[p];if(n){const t="y"===u?"bottom":"right";b=Wi(b+h["y"===u?"top":"left"],b,b-h[t])}if(a){const t="y"===p?"bottom":"right";f=Wi(f+h["y"===p?"top":"left"],f,f-h[t])}const v=l.fn(we(ye({},e),{[u]:b,[p]:f}));return we(ye({},v),{data:{x:v.x-i,y:v.y-o}})}}}({boundary:this.shiftBoundary,padding:this.shiftPadding})),this.autoSize?t.push(Ji({boundary:this.autoSizeBoundary,padding:this.autoSizePadding,apply:({availableWidth:t,availableHeight:e})=>{"vertical"===this.autoSize||"both"===this.autoSize?this.style.setProperty("--auto-size-available-height",`${e}px`):this.style.removeProperty("--auto-size-available-height"),"horizontal"===this.autoSize||"both"===this.autoSize?this.style.setProperty("--auto-size-available-width",`${t}px`):this.style.removeProperty("--auto-size-available-width")}})):(this.style.removeProperty("--auto-size-available-width"),this.style.removeProperty("--auto-size-available-height")),this.arrow&&t.push((t=>({name:"arrow",options:t,async fn(e){const{element:i,padding:o=0}=null!=t?t:{},{x:s,y:r,placement:n,rects:a,platform:l}=e;if(null==i)return{};const d=Mi(o),c={x:s,y:r},h=Fi(n),u=Ui(n),p=Bi(h),b=await l.getDimensions(i),f="y"===h?"top":"left",v="y"===h?"bottom":"right",m=a.reference[p]+a.reference[h]-c[h]-a.floating[p],g=c[h]-a.reference[h],y=await(null==l.getOffsetParent?void 0:l.getOffsetParent(i));let w=y?"y"===h?y.clientHeight||0:y.clientWidth||0:0;0===w&&(w=a.floating[p]);const _=m/2-g/2,$=d[f],x=w-b[p]-d[v],k=w/2-b[p]/2+_,A=Wi($,k,x),C=("start"===u?d[f]:d[v])>0&&k!==A&&a.reference[p]<=a.floating[p];return{[h]:c[h]-(C?k<$?$-k:x-k:0),data:{[h]:A,centerOffset:k-A}}}}))({element:this.arrowEl,padding:this.arrowPadding})),((t,e,i)=>(async(t,e,i)=>{const{placement:o="bottom",strategy:s="absolute",middleware:r=[],platform:n}=i,a=r.filter(Boolean),l=await(null==n.isRTL?void 0:n.isRTL(e));let d=await n.getElementRects({reference:t,floating:e,strategy:s}),{x:c,y:h}=Hi(d,o,l),u=o,p={},b=0;for(let i=0;i<a.length;i++){const{name:r,fn:f}=a[i],{x:v,y:m,data:g,reset:y}=await f({x:c,y:h,initialPlacement:o,placement:u,strategy:s,middlewareData:p,rects:d,platform:n,elements:{reference:t,floating:e}});c=null!=v?v:c,h=null!=m?m:h,p=we(ye({},p),{[r]:ye(ye({},p[r]),g)}),y&&b<=50&&(b++,"object"==typeof y&&(y.placement&&(u=y.placement),y.rects&&(d=!0===y.rects?await n.getElementRects({reference:t,floating:e,strategy:s}):y.rects),({x:c,y:h}=Hi(d,u,l))),i=-1)}return{x:c,y:h,placement:u,strategy:s,middlewareData:p}})(t,e,ye({platform:Eo},i)))(this.anchorEl,this.popup,{placement:this.placement,middleware:t,strategy:this.strategy}).then((({x:t,y:e,middlewareData:i,placement:o})=>{const s="rtl"===getComputedStyle(this).direction,r={top:"bottom",right:"left",bottom:"top",left:"right"}[o.split("-")[0]];if(this.setAttribute("data-current-placement",o),Object.assign(this.popup.style,{left:`${t}px`,top:`${e}px`}),this.arrow){const t=i.arrow.x,e=i.arrow.y;let o="",n="",a="",l="";if("start"===this.arrowPlacement){const i="number"==typeof t?`calc(${this.arrowPadding}px - var(--arrow-padding-offset))`:"";o="number"==typeof e?`calc(${this.arrowPadding}px - var(--arrow-padding-offset))`:"",n=s?i:"",l=s?"":i}else if("end"===this.arrowPlacement){const i="number"==typeof t?`calc(${this.arrowPadding}px - var(--arrow-padding-offset))`:"";n=s?"":i,l=s?i:"",a="number"==typeof e?`calc(${this.arrowPadding}px - var(--arrow-padding-offset))`:""}else"center"===this.arrowPlacement?(l="number"==typeof t?"calc(50% - var(--arrow-size-diagonal))":"",o="number"==typeof e?"calc(50% - var(--arrow-size-diagonal))":""):(l="number"==typeof t?`${t}px`:"",o="number"==typeof e?`${e}px`:"");Object.assign(this.arrowEl.style,{top:o,right:n,bottom:a,left:l,[r]:"calc(var(--arrow-size-diagonal) * -1)"})}})),this.emit("sl-reposition")}render(){return Ht`
      <slot name="anchor" @slotchange=${this.handleAnchorChange}></slot>

      <div
        part="popup"
        class=${li({popup:!0,"popup--active":this.active,"popup--fixed":"fixed"===this.strategy,"popup--has-arrow":this.arrow})}
      >
        <slot></slot>
        ${this.arrow?Ht`<div part="arrow" class="popup__arrow" role="presentation"></div>`:""}
      </div>
    `}};So.styles=Di,$e([Te(".popup")],So.prototype,"popup",2),$e([Te(".popup__arrow")],So.prototype,"arrowEl",2),$e([Ce()],So.prototype,"anchor",2),$e([Ce({type:Boolean,reflect:!0})],So.prototype,"active",2),$e([Ce({reflect:!0})],So.prototype,"placement",2),$e([Ce({reflect:!0})],So.prototype,"strategy",2),$e([Ce({type:Number})],So.prototype,"distance",2),$e([Ce({type:Number})],So.prototype,"skidding",2),$e([Ce({type:Boolean})],So.prototype,"arrow",2),$e([Ce({attribute:"arrow-placement"})],So.prototype,"arrowPlacement",2),$e([Ce({attribute:"arrow-padding",type:Number})],So.prototype,"arrowPadding",2),$e([Ce({type:Boolean})],So.prototype,"flip",2),$e([Ce({attribute:"flip-fallback-placements",converter:{fromAttribute:t=>t.split(" ").map((t=>t.trim())).filter((t=>""!==t)),toAttribute:t=>t.join(" ")}})],So.prototype,"flipFallbackPlacements",2),$e([Ce({attribute:"flip-fallback-strategy"})],So.prototype,"flipFallbackStrategy",2),$e([Ce({type:Object})],So.prototype,"flipBoundary",2),$e([Ce({attribute:"flip-padding",type:Number})],So.prototype,"flipPadding",2),$e([Ce({type:Boolean})],So.prototype,"shift",2),$e([Ce({type:Object})],So.prototype,"shiftBoundary",2),$e([Ce({attribute:"shift-padding",type:Number})],So.prototype,"shiftPadding",2),$e([Ce({attribute:"auto-size"})],So.prototype,"autoSize",2),$e([Ce()],So.prototype,"sync",2),$e([Ce({type:Object})],So.prototype,"autoSizeBoundary",2),$e([Ce({attribute:"auto-size-padding",type:Number})],So.prototype,"autoSizePadding",2),So=$e([ke("sl-popup")],So);const{I:To}=J,zo=t=>(...e)=>({_$litDirective$:t,values:e});class Po{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,i){this._$Ct=t,this._$AM=e,this._$Ci=i}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}}const Lo=(t,e)=>{var i,o;const s=t._$AN;if(void 0===s)return!1;for(const t of s)null===(o=(i=t)._$AO)||void 0===o||o.call(i,e,!1),Lo(t,e);return!0},Io=t=>{let e,i;do{if(void 0===(e=t._$AM))break;i=e._$AN,i.delete(t),t=e}while(0===(null==i?void 0:i.size))},Oo=t=>{for(let e;e=t._$AM;t=e){let i=e._$AN;if(void 0===i)e._$AN=i=new Set;else if(i.has(t))break;i.add(t),Uo(e)}};function Do(t){void 0!==this._$AN?(Io(this),this._$AM=t,Oo(this)):this._$AM=t}function Ro(t,e=!1,i=0){const o=this._$AH,s=this._$AN;if(void 0!==s&&0!==s.size)if(e)if(Array.isArray(o))for(let t=i;t<o.length;t++)Lo(o[t],!1),Io(o[t]);else null!=o&&(Lo(o,!1),Io(o));else Lo(this,t)}const Uo=t=>{var e,i,o,s;2==t.type&&(null!==(e=(o=t)._$AP)&&void 0!==e||(o._$AP=Ro),null!==(i=(s=t)._$AQ)&&void 0!==i||(s._$AQ=Do))};class Fo extends Po{constructor(){super(...arguments),this._$AN=void 0}_$AT(t,e,i){super._$AT(t,e,i),Oo(this),this.isConnected=t._$AU}_$AO(t,e=!0){var i,o;t!==this.isConnected&&(this.isConnected=t,t?null===(i=this.reconnected)||void 0===i||i.call(this):null===(o=this.disconnected)||void 0===o||o.call(this)),e&&(Lo(this,t),Io(this))}setValue(t){if((t=>void 0===this._$Ct.strings)())this._$Ct._$AI(t,this);else{const e=[...this._$Ct._$AH];e[this._$Ci]=t,this._$Ct._$AI(e,this,0)}}disconnected(){}reconnected(){}}class Bo{constructor(t){this.Y=t}disconnect(){this.Y=void 0}reconnect(t){this.Y=t}deref(){return this.Y}}class Ho{constructor(){this.Z=void 0,this.q=void 0}get(){return this.Z}pause(){var t;null!==(t=this.Z)&&void 0!==t||(this.Z=new Promise((t=>this.q=t)))}resume(){var t;null===(t=this.q)||void 0===t||t.call(this),this.Z=this.q=void 0}}const Mo=t=>!(t=>null===t||"object"!=typeof t&&"function"!=typeof t)(t)&&"function"==typeof t.then,No=zo(class extends Fo{constructor(){super(...arguments),this._$Cwt=1073741823,this._$Cyt=[],this._$CK=new Bo(this),this._$CX=new Ho}render(...t){var e;return null!==(e=t.find((t=>!Mo(t))))&&void 0!==e?e:U}update(t,e){const i=this._$Cyt;let o=i.length;this._$Cyt=e;const s=this._$CK,r=this._$CX;this.isConnected||this.disconnected();for(let t=0;t<e.length&&!(t>this._$Cwt);t++){const n=e[t];if(!Mo(n))return this._$Cwt=t,n;t<o&&n===i[t]||(this._$Cwt=1073741823,o=0,Promise.resolve(n).then((async t=>{for(;r.get();)await r.get();const e=s.deref();if(void 0!==e){const i=e._$Cyt.indexOf(n);i>-1&&i<e._$Cwt&&(e._$Cwt=i,e.setValue(t))}})))}return U}disconnected(){this._$CK.disconnect(),this._$CX.pause()}reconnected(){this._$CK.reconnect(this),this._$CX.resume()}});class Vo{constructor(t){this.message=t,this.name="InvalidTableFileException"}}class jo extends it{static properties={file:{type:File},template:{attribute:!1}};static styles=r`
        table {
            table-layout: fixed;
            border-collapse: collapse;
            width: auto;
        }

        table th, table td {
            font-family: Arial, sans-serif;
            overflow: hidden;
            word-break: normal;
            border-color: rgb(161, 161, 170);
            border-style: solid;
        }

        table th {
            font-size: 15px;
            font-weight: bold;
            padding: 10px 5px;
            border-width: 1px;
            text-align: center;
            background-color: rgb(161, 195, 209);
        }

        table td {
            font-size: 14px;
            padding: 5px 10px;
            border-width: 1px;
            background-color: rgb(237, 250, 255);
        }

        table .td-colname {
            font-size: 15px;
            font-weight: bold;
            text-align: left;
        }

        table .td-value {
            text-align: left;
        }

        table .td-funcname {
            text-align: left;
        }
    `;getWidth(t){return Math.min(100,20*(t-2))}async*makeTextFileLineIterator(t){const e=new TextDecoder("utf-8"),i=t.stream().getReader();let{value:o,done:s}=await i.read();o=o?e.decode(o,{stream:!0}):"";const r=/\r\n|\n|\r/gm;let n=0;for(;;){const t=r.exec(o);if(t)yield o.substring(n,t.index),n=r.lastIndex;else{if(s)break;const t=o.substr(n);({value:o,done:s}=await i.read()),o=t+(o?e.decode(o,{stream:!0}):""),n=r.lastIndex=0}}n<o.length&&(yield o.substr(n))}render(){if(!this.file)return R``;const t=this.parseSrc();return R`${No(t,R``)}`}}customElements.define("sc-report-table",jo),customElements.define("sc-intro-tbl",class extends jo{parseHeader(t){const e=t.split(";");return R`
            <tr>
                ${e.map((t=>R`<th>${t}</th>`))}
            </tr>
        `}parseRow(t){let e=R``,i=!0;for(const o of t.split(";")){const[t,s,r]=o.split("|");let n=R`${t}`;r&&(n=R`<a href=${r}>${n}</a>`),s&&(n=R`<abbr title=${s}>${n}</abbr>`),i?(e=R`${e}
                    <td class="td-colname">
                        ${n}
                    </td>
                `,i=!1):e=R`${e}
                    <td>
                        ${n}
                    </td>
                `}return R`<tr>${e}</tr>`}async parseSrc(){const t=this.makeTextFileLineIterator(this.file);let e=await t.next();if(e=e.value,!e.startsWith("H;"))throw new Vo("first line in intro table file should be a header.");e=e.slice(2);let i=this.parseHeader(e);for await(let e of t){if(!e.startsWith("R;"))throw new Vo("lines following the first should all be normal table rows.");e=e.slice(2),i=R`${i}${this.parseRow(e)}`}return R`<table>${i}</table>`}});var qo=ht`
  ${de}

  :host {
    display: contents;

    /* For better DX, we'll reset the margin here so the base part can inherit it */
    margin: 0;
  }

  .alert {
    position: relative;
    display: flex;
    align-items: stretch;
    background-color: var(--sl-panel-background-color);
    border: solid var(--sl-panel-border-width) var(--sl-panel-border-color);
    border-top-width: calc(var(--sl-panel-border-width) * 3);
    border-radius: var(--sl-border-radius-medium);
    font-family: var(--sl-font-sans);
    font-size: var(--sl-font-size-small);
    font-weight: var(--sl-font-weight-normal);
    line-height: 1.6;
    color: var(--sl-color-neutral-700);
    margin: inherit;
  }

  .alert:not(.alert--has-icon) .alert__icon,
  .alert:not(.alert--closable) .alert__close-button {
    display: none;
  }

  .alert__icon {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    font-size: var(--sl-font-size-large);
    padding-inline-start: var(--sl-spacing-large);
  }

  .alert--primary {
    border-top-color: var(--sl-color-primary-600);
  }

  .alert--primary .alert__icon {
    color: var(--sl-color-primary-600);
  }

  .alert--success {
    border-top-color: var(--sl-color-success-600);
  }

  .alert--success .alert__icon {
    color: var(--sl-color-success-600);
  }

  .alert--neutral {
    border-top-color: var(--sl-color-neutral-600);
  }

  .alert--neutral .alert__icon {
    color: var(--sl-color-neutral-600);
  }

  .alert--warning {
    border-top-color: var(--sl-color-warning-600);
  }

  .alert--warning .alert__icon {
    color: var(--sl-color-warning-600);
  }

  .alert--danger {
    border-top-color: var(--sl-color-danger-600);
  }

  .alert--danger .alert__icon {
    color: var(--sl-color-danger-600);
  }

  .alert__message {
    flex: 1 1 auto;
    display: block;
    padding: var(--sl-spacing-large);
    overflow: hidden;
  }

  .alert__close-button {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    font-size: var(--sl-font-size-medium);
    padding-inline-end: var(--sl-spacing-medium);
  }
`,Wo=Object.assign(document.createElement("div"),{className:"sl-toast-stack"}),Ko=class extends ze{constructor(){super(...arguments),this.hasSlotController=new si(this,"icon","suffix"),this.localize=new oi(this),this.open=!1,this.closable=!1,this.variant="primary",this.duration=1/0}firstUpdated(){this.base.hidden=!this.open}restartAutoHide(){clearTimeout(this.autoHideTimeout),this.open&&this.duration<1/0&&(this.autoHideTimeout=window.setTimeout((()=>this.hide()),this.duration))}handleCloseClick(){this.hide()}handleMouseMove(){this.restartAutoHide()}async handleOpenChange(){if(this.open){this.emit("sl-show"),this.duration<1/0&&this.restartAutoHide(),await Ne(this.base),this.base.hidden=!1;const{keyframes:t,options:e}=Ye(this,"alert.show",{dir:this.localize.dir()});await He(this.base,t,e),this.emit("sl-after-show")}else{this.emit("sl-hide"),clearTimeout(this.autoHideTimeout),await Ne(this.base);const{keyframes:t,options:e}=Ye(this,"alert.hide",{dir:this.localize.dir()});await He(this.base,t,e),this.base.hidden=!0,this.emit("sl-after-hide")}}handleDurationChange(){this.restartAutoHide()}async show(){if(!this.open)return this.open=!0,Be(this,"sl-after-show")}async hide(){if(this.open)return this.open=!1,Be(this,"sl-after-hide")}async toast(){return new Promise((t=>{null===Wo.parentElement&&document.body.append(Wo),Wo.appendChild(this),requestAnimationFrame((()=>{this.clientWidth,this.show()})),this.addEventListener("sl-after-hide",(()=>{Wo.removeChild(this),t(),null===Wo.querySelector("sl-alert")&&Wo.remove()}),{once:!0})}))}render(){return Ht`
      <div
        part="base"
        class=${li({alert:!0,"alert--open":this.open,"alert--closable":this.closable,"alert--has-icon":this.hasSlotController.test("icon"),"alert--primary":"primary"===this.variant,"alert--success":"success"===this.variant,"alert--neutral":"neutral"===this.variant,"alert--warning":"warning"===this.variant,"alert--danger":"danger"===this.variant})}
        role="alert"
        aria-hidden=${this.open?"false":"true"}
        @mousemove=${this.handleMouseMove}
      >
        <slot name="icon" part="icon" class="alert__icon"></slot>

        <slot part="message" class="alert__message" aria-live="polite"></slot>

        ${this.closable?Ht`
              <sl-icon-button
                part="close-button"
                exportparts="base:close-button__base"
                class="alert__close-button"
                name="x-lg"
                library="system"
                label=${this.localize.term("close")}
                @click=${this.handleCloseClick}
              ></sl-icon-button>
            `:""}
      </div>
    `}};Ko.styles=qo,$e([Te('[part~="base"]')],Ko.prototype,"base",2),$e([Ce({type:Boolean,reflect:!0})],Ko.prototype,"open",2),$e([Ce({type:Boolean,reflect:!0})],Ko.prototype,"closable",2),$e([Ce({reflect:!0})],Ko.prototype,"variant",2),$e([Ce({type:Number})],Ko.prototype,"duration",2),$e([xe("open",{waitUntilFirstUpdate:!0})],Ko.prototype,"handleOpenChange",1),$e([xe("duration")],Ko.prototype,"handleDurationChange",1),Ko=$e([ke("sl-alert")],Ko),Ke("alert.show",{keyframes:[{opacity:0,scale:.8},{opacity:1,scale:1}],options:{duration:250,easing:"ease"}}),Ke("alert.hide",{keyframes:[{opacity:1,scale:1},{opacity:0,scale:.8}],options:{duration:250,easing:"ease"}});var Yo=ht`
  ${de}

  :host {
    --indicator-color: var(--sl-color-primary-600);
    --track-color: var(--sl-color-neutral-200);
    --track-width: 2px;

    display: block;
  }

  .tab-group {
    display: flex;
    border-radius: 0;
  }

  .tab-group__tabs {
    display: flex;
    position: relative;
  }

  .tab-group__indicator {
    position: absolute;
    transition: var(--sl-transition-fast) translate ease, var(--sl-transition-fast) width ease;
  }

  .tab-group--has-scroll-controls .tab-group__nav-container {
    position: relative;
    padding: 0 var(--sl-spacing-x-large);
  }

  .tab-group__body {
    display: block;
    overflow: auto;
  }

  .tab-group__scroll-button {
    display: flex;
    align-items: center;
    justify-content: center;
    position: absolute;
    top: 0;
    bottom: 0;
    width: var(--sl-spacing-x-large);
  }

  .tab-group__scroll-button--start {
    left: 0;
  }

  .tab-group__scroll-button--end {
    right: 0;
  }

  .tab-group--rtl .tab-group__scroll-button--start {
    left: auto;
    right: 0;
  }

  .tab-group--rtl .tab-group__scroll-button--end {
    left: 0;
    right: auto;
  }

  /*
   * Top
   */

  .tab-group--top {
    flex-direction: column;
  }

  .tab-group--top .tab-group__nav-container {
    order: 1;
  }

  .tab-group--top .tab-group__nav {
    display: flex;
    overflow-x: auto;

    /* Hide scrollbar in Firefox */
    scrollbar-width: none;
  }

  /* Hide scrollbar in Chrome/Safari */
  .tab-group--top .tab-group__nav::-webkit-scrollbar {
    width: 0;
    height: 0;
  }

  .tab-group--top .tab-group__tabs {
    flex: 1 1 auto;
    position: relative;
    flex-direction: row;
    border-bottom: solid var(--track-width) var(--track-color);
  }

  .tab-group--top .tab-group__indicator {
    bottom: calc(-1 * var(--track-width));
    border-bottom: solid var(--track-width) var(--indicator-color);
  }

  .tab-group--top .tab-group__body {
    order: 2;
  }

  .tab-group--top ::slotted(sl-tab-panel) {
    --padding: var(--sl-spacing-medium) 0;
  }

  /*
   * Bottom
   */

  .tab-group--bottom {
    flex-direction: column;
  }

  .tab-group--bottom .tab-group__nav-container {
    order: 2;
  }

  .tab-group--bottom .tab-group__nav {
    display: flex;
    overflow-x: auto;

    /* Hide scrollbar in Firefox */
    scrollbar-width: none;
  }

  /* Hide scrollbar in Chrome/Safari */
  .tab-group--bottom .tab-group__nav::-webkit-scrollbar {
    width: 0;
    height: 0;
  }

  .tab-group--bottom .tab-group__tabs {
    flex: 1 1 auto;
    position: relative;
    flex-direction: row;
    border-top: solid var(--track-width) var(--track-color);
  }

  .tab-group--bottom .tab-group__indicator {
    top: calc(-1 * var(--track-width));
    border-top: solid var(--track-width) var(--indicator-color);
  }

  .tab-group--bottom .tab-group__body {
    order: 1;
  }

  .tab-group--bottom ::slotted(sl-tab-panel) {
    --padding: var(--sl-spacing-medium) 0;
  }

  /*
   * Start
   */

  .tab-group--start {
    flex-direction: row;
  }

  .tab-group--start .tab-group__nav-container {
    order: 1;
  }

  .tab-group--start .tab-group__tabs {
    flex: 0 0 auto;
    flex-direction: column;
    border-inline-end: solid var(--track-width) var(--track-color);
  }

  .tab-group--start .tab-group__indicator {
    right: calc(-1 * var(--track-width));
    border-right: solid var(--track-width) var(--indicator-color);
  }

  .tab-group--start.tab-group--rtl .tab-group__indicator {
    right: auto;
    left: calc(-1 * var(--track-width));
  }

  .tab-group--start .tab-group__body {
    flex: 1 1 auto;
    order: 2;
  }

  .tab-group--start ::slotted(sl-tab-panel) {
    --padding: 0 var(--sl-spacing-medium);
  }

  /*
   * End
   */

  .tab-group--end {
    flex-direction: row;
  }

  .tab-group--end .tab-group__nav-container {
    order: 2;
  }

  .tab-group--end .tab-group__tabs {
    flex: 0 0 auto;
    flex-direction: column;
    border-left: solid var(--track-width) var(--track-color);
  }

  .tab-group--end .tab-group__indicator {
    left: calc(-1 * var(--track-width));
    border-inline-start: solid var(--track-width) var(--indicator-color);
  }

  .tab-group--end.tab-group--rtl .tab-group__indicator {
    right: calc(-1 * var(--track-width));
    left: auto;
  }

  .tab-group--end .tab-group__body {
    flex: 1 1 auto;
    order: 1;
  }

  .tab-group--end ::slotted(sl-tab-panel) {
    --padding: 0 var(--sl-spacing-medium);
  }
`,Go=class extends ze{constructor(){super(...arguments),this.localize=new oi(this),this.tabs=[],this.panels=[],this.hasScrollControls=!1,this.placement="top",this.activation="auto",this.noScrollControls=!1}connectedCallback(){super.connectedCallback(),this.resizeObserver=new ResizeObserver((()=>{this.repositionIndicator(),this.updateScrollControls()})),this.mutationObserver=new MutationObserver((t=>{t.some((t=>!["aria-labelledby","aria-controls"].includes(t.attributeName)))&&setTimeout((()=>this.setAriaLabels())),t.some((t=>"disabled"===t.attributeName))&&this.syncTabsAndPanels()})),this.updateComplete.then((()=>{this.syncTabsAndPanels(),this.mutationObserver.observe(this,{attributes:!0,childList:!0,subtree:!0}),this.resizeObserver.observe(this.nav),new IntersectionObserver(((t,e)=>{var i;t[0].intersectionRatio>0&&(this.setAriaLabels(),this.setActiveTab(null!=(i=this.getActiveTab())?i:this.tabs[0],{emitEvents:!1}),e.unobserve(t[0].target))})).observe(this.tabGroup)}))}disconnectedCallback(){this.mutationObserver.disconnect(),this.resizeObserver.unobserve(this.nav)}getAllTabs(t={includeDisabled:!0}){return[...this.shadowRoot.querySelector('slot[name="nav"]').assignedElements()].filter((e=>t.includeDisabled?"sl-tab"===e.tagName.toLowerCase():"sl-tab"===e.tagName.toLowerCase()&&!e.disabled))}getAllPanels(){return[...this.body.assignedElements()].filter((t=>"sl-tab-panel"===t.tagName.toLowerCase()))}getActiveTab(){return this.tabs.find((t=>t.active))}handleClick(t){const e=t.target.closest("sl-tab");(null==e?void 0:e.closest("sl-tab-group"))===this&&null!==e&&this.setActiveTab(e,{scrollBehavior:"smooth"})}handleKeyDown(t){const e=t.target.closest("sl-tab");if((null==e?void 0:e.closest("sl-tab-group"))===this&&(["Enter"," "].includes(t.key)&&null!==e&&(this.setActiveTab(e,{scrollBehavior:"smooth"}),t.preventDefault()),["ArrowLeft","ArrowRight","ArrowUp","ArrowDown","Home","End"].includes(t.key))){const e=this.tabs.find((t=>t.matches(":focus"))),i="rtl"===this.localize.dir();if("sl-tab"===(null==e?void 0:e.tagName.toLowerCase())){let o=this.tabs.indexOf(e);"Home"===t.key?o=0:"End"===t.key?o=this.tabs.length-1:["top","bottom"].includes(this.placement)&&t.key===(i?"ArrowRight":"ArrowLeft")||["start","end"].includes(this.placement)&&"ArrowUp"===t.key?o--:(["top","bottom"].includes(this.placement)&&t.key===(i?"ArrowLeft":"ArrowRight")||["start","end"].includes(this.placement)&&"ArrowDown"===t.key)&&o++,o<0&&(o=this.tabs.length-1),o>this.tabs.length-1&&(o=0),this.tabs[o].focus({preventScroll:!0}),"auto"===this.activation&&this.setActiveTab(this.tabs[o],{scrollBehavior:"smooth"}),["top","bottom"].includes(this.placement)&&Ue(this.tabs[o],this.nav,"horizontal"),t.preventDefault()}}}handleScrollToStart(){this.nav.scroll({left:"rtl"===this.localize.dir()?this.nav.scrollLeft+this.nav.clientWidth:this.nav.scrollLeft-this.nav.clientWidth,behavior:"smooth"})}handleScrollToEnd(){this.nav.scroll({left:"rtl"===this.localize.dir()?this.nav.scrollLeft-this.nav.clientWidth:this.nav.scrollLeft+this.nav.clientWidth,behavior:"smooth"})}setActiveTab(t,e){if(e=ye({emitEvents:!0,scrollBehavior:"auto"},e),t!==this.activeTab&&!t.disabled){const i=this.activeTab;this.activeTab=t,this.tabs.map((t=>t.active=t===this.activeTab)),this.panels.map((t=>{var e;return t.active=t.name===(null==(e=this.activeTab)?void 0:e.panel)})),this.syncIndicator(),["top","bottom"].includes(this.placement)&&Ue(this.activeTab,this.nav,"horizontal",e.scrollBehavior),e.emitEvents&&(i&&this.emit("sl-tab-hide",{detail:{name:i.panel}}),this.emit("sl-tab-show",{detail:{name:this.activeTab.panel}}))}}setAriaLabels(){this.tabs.forEach((t=>{const e=this.panels.find((e=>e.name===t.panel));e&&(t.setAttribute("aria-controls",e.getAttribute("id")),e.setAttribute("aria-labelledby",t.getAttribute("id")))}))}repositionIndicator(){const t=this.getActiveTab();if(!t)return;const e=t.clientWidth,i=t.clientHeight,o="rtl"===this.localize.dir(),s=this.getAllTabs(),r=s.slice(0,s.indexOf(t)).reduce(((t,e)=>({left:t.left+e.clientWidth,top:t.top+e.clientHeight})),{left:0,top:0});switch(this.placement){case"top":case"bottom":this.indicator.style.width=`${e}px`,this.indicator.style.height="auto",this.indicator.style.translate=o?-1*r.left+"px":`${r.left}px`;break;case"start":case"end":this.indicator.style.width="auto",this.indicator.style.height=`${i}px`,this.indicator.style.translate=`0 ${r.top}px`}}syncTabsAndPanels(){this.tabs=this.getAllTabs({includeDisabled:!1}),this.panels=this.getAllPanels(),this.syncIndicator()}updateScrollControls(){this.noScrollControls?this.hasScrollControls=!1:this.hasScrollControls=["top","bottom"].includes(this.placement)&&this.nav.scrollWidth>this.nav.clientWidth}syncIndicator(){this.getActiveTab()?(this.indicator.style.display="block",this.repositionIndicator()):this.indicator.style.display="none"}show(t){const e=this.tabs.find((e=>e.panel===t));e&&this.setActiveTab(e,{scrollBehavior:"smooth"})}render(){const t="rtl"===this.localize.dir();return Ht`
      <div
        part="base"
        class=${li({"tab-group":!0,"tab-group--top":"top"===this.placement,"tab-group--bottom":"bottom"===this.placement,"tab-group--start":"start"===this.placement,"tab-group--end":"end"===this.placement,"tab-group--rtl":"rtl"===this.localize.dir(),"tab-group--has-scroll-controls":this.hasScrollControls})}
        @click=${this.handleClick}
        @keydown=${this.handleKeyDown}
      >
        <div class="tab-group__nav-container" part="nav">
          ${this.hasScrollControls?Ht`
                <sl-icon-button
                  part="scroll-button scroll-button--start"
                  exportparts="base:scroll-button__base"
                  class="tab-group__scroll-button tab-group__scroll-button--start"
                  name=${t?"chevron-right":"chevron-left"}
                  library="system"
                  label=${this.localize.term("scrollToStart")}
                  @click=${this.handleScrollToStart}
                ></sl-icon-button>
              `:""}

          <div class="tab-group__nav">
            <div part="tabs" class="tab-group__tabs" role="tablist">
              <div part="active-tab-indicator" class="tab-group__indicator"></div>
              <slot name="nav" @slotchange=${this.syncTabsAndPanels}></slot>
            </div>
          </div>

          ${this.hasScrollControls?Ht`
                <sl-icon-button
                  part="scroll-button scroll-button--end"
                  exportparts="base:scroll-button__base"
                  class="tab-group__scroll-button tab-group__scroll-button--end"
                  name=${t?"chevron-left":"chevron-right"}
                  library="system"
                  label=${this.localize.term("scrollToEnd")}
                  @click=${this.handleScrollToEnd}
                ></sl-icon-button>
              `:""}
        </div>

        <slot part="body" class="tab-group__body" @slotchange=${this.syncTabsAndPanels}></slot>
      </div>
    `}};Go.styles=Yo,$e([Te(".tab-group")],Go.prototype,"tabGroup",2),$e([Te(".tab-group__body")],Go.prototype,"body",2),$e([Te(".tab-group__nav")],Go.prototype,"nav",2),$e([Te(".tab-group__indicator")],Go.prototype,"indicator",2),$e([Ee()],Go.prototype,"hasScrollControls",2),$e([Ce()],Go.prototype,"placement",2),$e([Ce()],Go.prototype,"activation",2),$e([Ce({attribute:"no-scroll-controls",type:Boolean})],Go.prototype,"noScrollControls",2),$e([xe("noScrollControls",{waitUntilFirstUpdate:!0})],Go.prototype,"updateScrollControls",1),$e([xe("placement",{waitUntilFirstUpdate:!0})],Go.prototype,"syncIndicator",1),Go=$e([ke("sl-tab-group")],Go);var Zo=ht`
  ${de}

  :host {
    display: inline-block;
  }

  .tab {
    display: inline-flex;
    align-items: center;
    font-family: var(--sl-font-sans);
    font-size: var(--sl-font-size-small);
    font-weight: var(--sl-font-weight-semibold);
    border-radius: var(--sl-border-radius-medium);
    color: var(--sl-color-neutral-600);
    padding: var(--sl-spacing-medium) var(--sl-spacing-large);
    white-space: nowrap;
    user-select: none;
    cursor: pointer;
    transition: var(--transition-speed) box-shadow, var(--transition-speed) color;
  }

  .tab:hover:not(.tab--disabled) {
    color: var(--sl-color-primary-600);
  }

  .tab:focus {
    outline: none;
  }

  .tab:focus-visible:not(.tab--disabled) {
    color: var(--sl-color-primary-600);
  }

  .tab:focus-visible {
    outline: var(--sl-focus-ring);
    outline-offset: calc(-1 * var(--sl-focus-ring-width) - var(--sl-focus-ring-offset));
  }

  .tab.tab--active:not(.tab--disabled) {
    color: var(--sl-color-primary-600);
  }

  .tab.tab--closable {
    padding-inline-end: var(--sl-spacing-small);
  }

  .tab.tab--disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .tab__close-button {
    font-size: var(--sl-font-size-small);
    margin-inline-start: var(--sl-spacing-small);
  }

  .tab__close-button::part(base) {
    padding: var(--sl-spacing-3x-small);
  }

  @media (forced-colors: active) {
    .tab.tab--active:not(.tab--disabled) {
      outline: solid 1px transparent;
      outline-offset: -3px;
    }
  }
`,Xo=0,Jo=class extends ze{constructor(){super(...arguments),this.localize=new oi(this),this.attrId=++Xo,this.componentId=`sl-tab-${this.attrId}`,this.panel="",this.active=!1,this.closable=!1,this.disabled=!1}connectedCallback(){super.connectedCallback(),this.setAttribute("role","tab")}handleCloseClick(){this.emit("sl-close")}handleActiveChange(){this.setAttribute("aria-selected",this.active?"true":"false")}handleDisabledChange(){this.setAttribute("aria-disabled",this.disabled?"true":"false")}focus(t){this.tab.focus(t)}blur(){this.tab.blur()}render(){return this.id=this.id.length>0?this.id:this.componentId,Ht`
      <div
        part="base"
        class=${li({tab:!0,"tab--active":this.active,"tab--closable":this.closable,"tab--disabled":this.disabled})}
        tabindex=${this.disabled?"-1":"0"}
      >
        <slot></slot>
        ${this.closable?Ht`
              <sl-icon-button
                part="close-button"
                exportparts="base:close-button__base"
                name="x-lg"
                library="system"
                label=${this.localize.term("close")}
                class="tab__close-button"
                @click=${this.handleCloseClick}
                tabindex="-1"
              ></sl-icon-button>
            `:""}
      </div>
    `}};Jo.styles=Zo,$e([Te(".tab")],Jo.prototype,"tab",2),$e([Ce({reflect:!0})],Jo.prototype,"panel",2),$e([Ce({type:Boolean,reflect:!0})],Jo.prototype,"active",2),$e([Ce({type:Boolean})],Jo.prototype,"closable",2),$e([Ce({type:Boolean,reflect:!0})],Jo.prototype,"disabled",2),$e([xe("active")],Jo.prototype,"handleActiveChange",1),$e([xe("disabled")],Jo.prototype,"handleDisabledChange",1),Jo=$e([ke("sl-tab")],Jo);var Qo=ht`
  ${de}

  :host {
    --padding: 0;

    display: block;
  }

  .tab-panel {
    display: block;
    padding: var(--padding);
  }

  .tab-panel:not(.tab-panel--active) {
    display: none;
  }
`,ts=0,es=class extends ze{constructor(){super(...arguments),this.attrId=++ts,this.componentId=`sl-tab-panel-${this.attrId}`,this.name="",this.active=!1}connectedCallback(){super.connectedCallback(),this.id=this.id.length>0?this.id:this.componentId,this.setAttribute("role","tabpanel")}handleActiveChange(){this.setAttribute("aria-hidden",this.active?"false":"true")}render(){return Ht`
      <slot
        part="base"
        class=${li({"tab-panel":!0,"tab-panel--active":this.active})}
      ></slot>
    `}};es.styles=Qo,$e([Ce({reflect:!0})],es.prototype,"name",2),$e([Ce({type:Boolean,reflect:!0})],es.prototype,"active",2),$e([xe("active")],es.prototype,"handleActiveChange",1),es=$e([ke("sl-tab-panel")],es);var is=ht`
  ${de}

  :host {
    /*
     * These are actually used by tree item, but we define them here so they can more easily be set and all tree items
     * stay consistent.
     */
    --indent-guide-color: var(--sl-color-neutral-200);
    --indent-guide-offset: 0;
    --indent-guide-style: solid;
    --indent-guide-width: 0;
    --indent-size: var(--sl-spacing-large);

    display: block;
    isolation: isolate;

    /*
     * Tree item indentation uses the "em" unit to increment its width on each level, so setting the font size to zero
     * here removes the indentation for all the nodes on the first level.
     */
    font-size: 0;
  }
`,os=ht`
  ${de}

  :host {
    display: block;
    outline: 0;
    z-index: 0;
  }

  :host(:focus) {
    outline: none;
  }

  slot:not([name])::slotted(sl-icon) {
    margin-inline-end: var(--sl-spacing-x-small);
  }

  .tree-item {
    position: relative;
    display: flex;
    align-items: stretch;
    flex-direction: column;
    color: var(--sl-color-neutral-700);
    cursor: pointer;
    user-select: none;
    white-space: nowrap;
  }

  .tree-item__checkbox {
    pointer-events: none;
  }

  .tree-item__expand-button,
  .tree-item__checkbox,
  .tree-item__label {
    font-family: var(--sl-font-sans);
    font-size: var(--sl-font-size-medium);
    font-weight: var(--sl-font-weight-normal);
    line-height: var(--sl-line-height-normal);
    letter-spacing: var(--sl-letter-spacing-normal);
  }

  .tree-item__checkbox::part(base) {
    display: flex;
    align-items: center;
  }

  .tree-item__indentation {
    display: block;
    width: 1em;
    flex-shrink: 0;
  }

  .tree-item__expand-button {
    display: flex;
    align-items: center;
    justify-content: center;
    box-sizing: content-box;
    color: var(--sl-color-neutral-500);
    padding: var(--sl-spacing-x-small);
    width: 1rem;
    height: 1rem;
    cursor: pointer;
  }

  .tree-item__expand-button {
    transition: var(--sl-transition-medium) rotate ease;
  }

  .tree-item--expanded .tree-item__expand-button {
    rotate: 90deg;
  }

  .tree-item--expanded.tree-item--rtl .tree-item__expand-button {
    rotate: -90deg;
  }

  .tree-item--expanded slot[name='expand-icon'],
  .tree-item:not(.tree-item--expanded) slot[name='collapse-icon'] {
    display: none;
  }

  .tree-item:not(.tree-item--has-expand-button) .tree-item__expand-icon-slot {
    display: none;
  }

  .tree-item__expand-button--visible {
    cursor: pointer;
  }

  .tree-item__item {
    display: flex;
    align-items: center;
    border-inline-start: solid 3px transparent;
  }

  .tree-item--disabled .tree-item__item {
    opacity: 0.5;
    outline: none;
    cursor: not-allowed;
  }

  :host(:focus-visible) .tree-item__item {
    outline: var(--sl-focus-ring);
    outline-offset: var(--sl-focus-ring-offset);
    z-index: 2;
  }

  :host(:not([aria-disabled='true'])) .tree-item--selected .tree-item__item {
    background-color: var(--sl-color-neutral-100);
    border-inline-start-color: var(--sl-color-primary-600);
  }

  :host(:not([aria-disabled='true'])) .tree-item__expand-button {
    color: var(--sl-color-neutral-600);
  }

  .tree-item__label {
    display: flex;
    align-items: center;
    transition: var(--sl-transition-fast) color;
  }

  .tree-item__children {
    display: block;
    font-size: calc(1em + var(--indent-size, var(--sl-spacing-medium)));
  }

  /* Indentation lines */
  .tree-item__children {
    position: relative;
  }

  .tree-item__children::before {
    content: '';
    position: absolute;
    top: var(--indent-guide-offset);
    bottom: var(--indent-guide-offset);
    left: calc(1em - (var(--indent-guide-width) / 2) - 1px);
    border-inline-end: var(--indent-guide-width) var(--indent-guide-style) var(--indent-guide-color);
    z-index: 1;
  }

  .tree-item--rtl .tree-item__children::before {
    left: auto;
    right: 1em;
  }

  @media (forced-colors: active) {
    :host(:not([aria-disabled='true'])) .tree-item--selected .tree-item__item {
      outline: dashed 1px SelectedItem;
    }
  }
`,{I:ss}=oe,rs={},ns=ni(class extends ai{constructor(t){if(super(t),3!==t.type&&1!==t.type&&4!==t.type)throw Error("The `live` directive is not allowed on child or event bindings");if(!(t=>void 0===t.strings)(t))throw Error("`live` bindings can only contain a single expression")}render(t){return t}update(t,[e]){if(e===Nt||e===Vt)return e;const i=t.element,o=t.name;if(3===t.type){if(e===i[o])return Nt}else if(4===t.type){if(!!e===i.hasAttribute(o))return Nt}else if(1===t.type&&i.getAttribute(o)===e+"")return Nt;return((t,e=rs)=>{t._$AH=e})(t),e}});function as(t,e,i){return t?e():null==i?void 0:i()}var ls=class extends ze{constructor(){super(...arguments),this.localize=new oi(this),this.indeterminate=!1,this.isLeaf=!1,this.loading=!1,this.selectable=!1,this.expanded=!1,this.selected=!1,this.disabled=!1,this.lazy=!1}static isTreeItem(t){return t instanceof Element&&"treeitem"===t.getAttribute("role")}connectedCallback(){super.connectedCallback(),this.setAttribute("role","treeitem"),this.setAttribute("tabindex","-1"),this.isNestedItem()&&(this.slot="children")}firstUpdated(){this.childrenContainer.hidden=!this.expanded,this.childrenContainer.style.height=this.expanded?"auto":"0",this.isLeaf=!this.lazy&&0===this.getChildrenItems().length,this.handleExpandedChange()}async animateCollapse(){this.emit("sl-collapse"),await Ne(this.childrenContainer);const{keyframes:t,options:e}=Ye(this,"tree-item.collapse",{dir:this.localize.dir()});await He(this.childrenContainer,Ve(t,this.childrenContainer.scrollHeight),e),this.childrenContainer.hidden=!0,this.emit("sl-after-collapse")}isNestedItem(){const t=this.parentElement;return!!t&&ls.isTreeItem(t)}handleChildrenSlotChange(){this.loading=!1,this.isLeaf=!this.lazy&&0===this.getChildrenItems().length}willUpdate(t){t.has("selected")&&!t.has("indeterminate")&&(this.indeterminate=!1)}async animateExpand(){this.emit("sl-expand"),await Ne(this.childrenContainer),this.childrenContainer.hidden=!1;const{keyframes:t,options:e}=Ye(this,"tree-item.expand",{dir:this.localize.dir()});await He(this.childrenContainer,Ve(t,this.childrenContainer.scrollHeight),e),this.childrenContainer.style.height="auto",this.emit("sl-after-expand")}handleLoadingChange(){this.setAttribute("aria-busy",this.loading?"true":"false"),this.loading||this.animateExpand()}handleDisabledChange(){this.setAttribute("aria-disabled",this.disabled?"true":"false")}handleSelectedChange(){this.setAttribute("aria-selected",this.selected?"true":"false")}handleExpandedChange(){this.isLeaf?this.removeAttribute("aria-expanded"):this.setAttribute("aria-expanded",this.expanded?"true":"false")}handleExpandAnimation(){this.expanded?this.lazy?(this.loading=!0,this.emit("sl-lazy-load")):this.animateExpand():this.animateCollapse()}handleLazyChange(){this.emit("sl-lazy-change")}getChildrenItems({includeDisabled:t=!0}={}){return this.childrenSlot?[...this.childrenSlot.assignedElements({flatten:!0})].filter((e=>ls.isTreeItem(e)&&(t||!e.disabled))):[]}render(){const t="rtl"===this.localize.dir(),e=!this.loading&&(!this.isLeaf||this.lazy);return Ht`
      <div
        part="base"
        class="${li({"tree-item":!0,"tree-item--expanded":this.expanded,"tree-item--selected":this.selected,"tree-item--disabled":this.disabled,"tree-item--leaf":this.isLeaf,"tree-item--has-expand-button":e,"tree-item--rtl":"rtl"===this.localize.dir()})}"
      >
        <div
          class="tree-item__item"
          part="
            item
            ${this.disabled?"item--disabled":""}
            ${this.expanded?"item--expanded":""}
            ${this.indeterminate?"item--indeterminate":""}
            ${this.selected?"item--selected":""}
          "
        >
          <div class="tree-item__indentation" part="indentation"></div>

          <div
            part="expand-button"
            class=${li({"tree-item__expand-button":!0,"tree-item__expand-button--visible":e})}
            aria-hidden="true"
          >
            ${as(this.loading,(()=>Ht` <sl-spinner></sl-spinner> `))}
            <slot class="tree-item__expand-icon-slot" name="expand-icon">
              <sl-icon library="system" name=${t?"chevron-left":"chevron-right"}></sl-icon>
            </slot>
            <slot class="tree-item__expand-icon-slot" name="collapse-icon">
              <sl-icon library="system" name=${t?"chevron-left":"chevron-right"}></sl-icon>
            </slot>
          </div>

          ${as(this.selectable,(()=>Ht`
                <sl-checkbox
                  tabindex="-1"
                  class="tree-item__checkbox"
                  ?disabled="${this.disabled}"
                  ?checked="${ns(this.selected)}"
                  ?indeterminate="${this.indeterminate}"
                >
                  <slot class="tree-item__label" part="label"></slot>
                </sl-checkbox>
              `),(()=>Ht` <slot class="tree-item__label" part="label"></slot> `))}
        </div>

        <slot
          name="children"
          class="tree-item__children"
          part="children"
          role="group"
          @slotchange="${this.handleChildrenSlotChange}"
        ></slot>
      </div>
    `}};function ds(t,e,i){return t<e?e:t>i?i:t}function cs(t,e=!1){function i(t){const e=t.getChildrenItems({includeDisabled:!1});if(e.length){const i=e.every((t=>t.selected)),o=e.every((t=>!t.selected&&!t.indeterminate));t.selected=i,t.indeterminate=!i&&!o}}!function t(o){for(const i of o.getChildrenItems())i.selected=e?o.selected||i.selected:!i.disabled&&o.selected,t(i);e&&i(o)}(t),function t(e){const o=e.parentElement;ls.isTreeItem(o)&&(i(o),t(o))}(t)}ls.styles=os,$e([Ee()],ls.prototype,"indeterminate",2),$e([Ee()],ls.prototype,"isLeaf",2),$e([Ee()],ls.prototype,"loading",2),$e([Ee()],ls.prototype,"selectable",2),$e([Ce({type:Boolean,reflect:!0})],ls.prototype,"expanded",2),$e([Ce({type:Boolean,reflect:!0})],ls.prototype,"selected",2),$e([Ce({type:Boolean,reflect:!0})],ls.prototype,"disabled",2),$e([Ce({type:Boolean,reflect:!0})],ls.prototype,"lazy",2),$e([Te("slot:not([name])")],ls.prototype,"defaultSlot",2),$e([Te("slot[name=children]")],ls.prototype,"childrenSlot",2),$e([Te(".tree-item__item")],ls.prototype,"itemElement",2),$e([Te(".tree-item__children")],ls.prototype,"childrenContainer",2),$e([Te(".tree-item__expand-button slot")],ls.prototype,"expandButtonSlot",2),$e([xe("loading",{waitUntilFirstUpdate:!0})],ls.prototype,"handleLoadingChange",1),$e([xe("disabled")],ls.prototype,"handleDisabledChange",1),$e([xe("selected")],ls.prototype,"handleSelectedChange",1),$e([xe("expanded",{waitUntilFirstUpdate:!0})],ls.prototype,"handleExpandedChange",1),$e([xe("expanded",{waitUntilFirstUpdate:!0})],ls.prototype,"handleExpandAnimation",1),$e([xe("lazy",{waitUntilFirstUpdate:!0})],ls.prototype,"handleLazyChange",1),ls=$e([ke("sl-tree-item")],ls),Ke("tree-item.expand",{keyframes:[{height:"0",opacity:"0",overflow:"hidden"},{height:"auto",opacity:"1",overflow:"hidden"}],options:{duration:250,easing:"cubic-bezier(0.4, 0.0, 0.2, 1)"}}),Ke("tree-item.collapse",{keyframes:[{height:"auto",opacity:"1",overflow:"hidden"},{height:"0",opacity:"0",overflow:"hidden"}],options:{duration:200,easing:"cubic-bezier(0.4, 0.0, 0.2, 1)"}});var hs=class extends ze{constructor(){super(...arguments),this.selection="single",this.localize=new oi(this),this.initTreeItem=t=>{t.selectable="multiple"===this.selection,["expand","collapse"].filter((t=>!!this.querySelector(`[slot="${t}-icon"]`))).forEach((e=>{const i=t.querySelector(`[slot="${e}-icon"]`);null===i?t.append(this.getExpandButtonIcon(e)):i.hasAttribute("data-default")&&i.replaceWith(this.getExpandButtonIcon(e))}))}}async connectedCallback(){super.connectedCallback(),this.handleTreeChanged=this.handleTreeChanged.bind(this),this.handleFocusIn=this.handleFocusIn.bind(this),this.handleFocusOut=this.handleFocusOut.bind(this),this.setAttribute("role","tree"),this.setAttribute("tabindex","0"),this.addEventListener("focusin",this.handleFocusIn),this.addEventListener("focusout",this.handleFocusOut),this.addEventListener("sl-lazy-change",this.handleSlotChange),await this.updateComplete,this.mutationObserver=new MutationObserver(this.handleTreeChanged),this.mutationObserver.observe(this,{childList:!0,subtree:!0})}disconnectedCallback(){super.disconnectedCallback(),this.mutationObserver.disconnect(),this.removeEventListener("focusin",this.handleFocusIn),this.removeEventListener("focusout",this.handleFocusOut),this.removeEventListener("sl-lazy-change",this.handleSlotChange)}getExpandButtonIcon(t){const e=("expand"===t?this.expandedIconSlot:this.collapsedIconSlot).assignedElements({flatten:!0})[0];if(e){const i=e.cloneNode(!0);return[i,...i.querySelectorAll("[id]")].forEach((t=>t.removeAttribute("id"))),i.setAttribute("data-default",""),i.slot=`${t}-icon`,i}return null}handleTreeChanged(t){for(const e of t){const t=[...e.addedNodes].filter(ls.isTreeItem),i=[...e.removedNodes].filter(ls.isTreeItem);t.forEach(this.initTreeItem),i.includes(this.lastFocusedItem)&&this.focusItem(this.getFocusableItems()[0])}}syncTreeItems(t){const e=this.getAllTreeItems();if("multiple"===this.selection)cs(t);else for(const i of e)i!==t&&(i.selected=!1)}selectItem(t){const e=[...this.selectedItems];"multiple"===this.selection?(t.selected=!t.selected,t.lazy&&(t.expanded=!0),this.syncTreeItems(t)):"single"===this.selection||t.isLeaf?(t.expanded=!t.expanded,t.selected=!0,this.syncTreeItems(t)):"leaf"===this.selection&&(t.expanded=!t.expanded);const i=this.selectedItems;(e.length!==i.length||i.some((t=>!e.includes(t))))&&Promise.all(i.map((t=>t.updateComplete))).then((()=>{this.emit("sl-selection-change",{detail:{selection:i}})}))}get selectedItems(){return this.getAllTreeItems().filter((t=>t.selected))}getAllTreeItems(){return[...this.querySelectorAll("sl-tree-item")]}getFocusableItems(){const t=this.getAllTreeItems(),e=new Set;return t.filter((t=>{var i;if(t.disabled)return!1;const o=null==(i=t.parentElement)?void 0:i.closest("[role=treeitem]");return o&&(!o.expanded||o.loading||e.has(o))&&e.add(t),!e.has(t)}))}focusItem(t){null==t||t.focus()}handleKeyDown(t){if(!["ArrowDown","ArrowUp","ArrowRight","ArrowLeft","Home","End","Enter"," "].includes(t.key))return;const e=this.getFocusableItems(),i="ltr"===this.localize.dir(),o="rtl"===this.localize.dir();if(e.length>0){t.preventDefault();const s=e.findIndex((t=>t.matches(":focus"))),r=e[s],n=t=>{const i=e[ds(t,0,e.length-1)];this.focusItem(i)},a=t=>{r.expanded=t};"ArrowDown"===t.key?n(s+1):"ArrowUp"===t.key?n(s-1):i&&"ArrowRight"===t.key||o&&"ArrowLeft"===t.key?!r||r.disabled||r.expanded||r.isLeaf&&!r.lazy?n(s+1):a(!0):i&&"ArrowLeft"===t.key||o&&"ArrowRight"===t.key?!r||r.disabled||r.isLeaf||!r.expanded?n(s-1):a(!1):"Home"===t.key?n(0):"End"===t.key?n(e.length-1):"Enter"!==t.key&&" "!==t.key||r.disabled||this.selectItem(r)}}handleClick(t){const e=t.target.closest("sl-tree-item"),i=t.composedPath().some((t=>{var e;return null==(e=null==t?void 0:t.classList)?void 0:e.contains("tree-item__expand-button")}));e&&!e.disabled&&("multiple"===this.selection&&i?e.expanded=!e.expanded:this.selectItem(e))}handleFocusOut(t){const e=t.relatedTarget;e&&this.contains(e)||(this.tabIndex=0)}handleFocusIn(t){const e=t.target;t.target===this&&this.focusItem(this.lastFocusedItem||this.getAllTreeItems()[0]),ls.isTreeItem(e)&&!e.disabled&&(this.lastFocusedItem&&(this.lastFocusedItem.tabIndex=-1),this.lastFocusedItem=e,this.tabIndex=-1,e.tabIndex=0)}handleSlotChange(){this.getAllTreeItems().forEach(this.initTreeItem)}async handleSelectionChange(){const t="multiple"===this.selection,e=this.getAllTreeItems();this.setAttribute("aria-multiselectable",t?"true":"false");for(const i of e)i.selectable=t;t&&(await this.updateComplete,[...this.querySelectorAll(":scope > sl-tree-item")].forEach((t=>cs(t,!0))))}render(){return Ht`
      <div part="base" class="tree" @click=${this.handleClick} @keydown=${this.handleKeyDown}>
        <slot @slotchange=${this.handleSlotChange}></slot>
        <slot name="expand-icon" hidden aria-hidden="true"> </slot>
        <slot name="collapse-icon" hidden aria-hidden="true"> </slot>
      </div>
    `}};hs.styles=is,$e([Te("slot:not([name])")],hs.prototype,"defaultSlot",2),$e([Te("slot[name=expand-icon]")],hs.prototype,"expandedIconSlot",2),$e([Te("slot[name=collapse-icon]")],hs.prototype,"collapsedIconSlot",2),$e([Ce()],hs.prototype,"selection",2),$e([xe("selection")],hs.prototype,"handleSelectionChange",1),hs=$e([ke("sl-tree")],hs);var us=ht`
  ${de}

  :host {
    display: inline-block;
  }

  .checkbox {
    display: inline-flex;
    align-items: top;
    font-family: var(--sl-input-font-family);
    font-weight: var(--sl-input-font-weight);
    color: var(--sl-input-color);
    vertical-align: middle;
    cursor: pointer;
  }

  .checkbox--small {
    --toggle-size: var(--sl-toggle-size-small);
    font-size: var(--sl-input-font-size-small);
  }

  .checkbox--medium {
    --toggle-size: var(--sl-toggle-size-medium);
    font-size: var(--sl-input-font-size-medium);
  }

  .checkbox--large {
    --toggle-size: var(--sl-toggle-size-large);
    font-size: var(--sl-input-font-size-large);
  }

  .checkbox__control {
    flex: 0 0 auto;
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: var(--toggle-size);
    height: var(--toggle-size);
    border: solid var(--sl-input-border-width) var(--sl-input-border-color);
    border-radius: 2px;
    background-color: var(--sl-input-background-color);
    color: var(--sl-color-neutral-0);
    transition: var(--sl-transition-fast) border-color, var(--sl-transition-fast) background-color,
      var(--sl-transition-fast) color, var(--sl-transition-fast) box-shadow;
  }

  .checkbox__input {
    position: absolute;
    opacity: 0;
    padding: 0;
    margin: 0;
    pointer-events: none;
  }

  .checkbox__checked-icon,
  .checkbox__indeterminate-icon {
    display: inline-flex;
    width: var(--toggle-size);
    height: var(--toggle-size);
  }

  /* Hover */
  .checkbox:not(.checkbox--checked):not(.checkbox--disabled) .checkbox__control:hover {
    border-color: var(--sl-input-border-color-hover);
    background-color: var(--sl-input-background-color-hover);
  }

  /* Focus */
  .checkbox:not(.checkbox--checked):not(.checkbox--disabled) .checkbox__input:focus-visible ~ .checkbox__control {
    outline: var(--sl-focus-ring);
    outline-offset: var(--sl-focus-ring-offset);
  }

  /* Checked/indeterminate */
  .checkbox--checked .checkbox__control,
  .checkbox--indeterminate .checkbox__control {
    border-color: var(--sl-color-primary-600);
    background-color: var(--sl-color-primary-600);
  }

  /* Checked/indeterminate + hover */
  .checkbox.checkbox--checked:not(.checkbox--disabled) .checkbox__control:hover,
  .checkbox.checkbox--indeterminate:not(.checkbox--disabled) .checkbox__control:hover {
    border-color: var(--sl-color-primary-500);
    background-color: var(--sl-color-primary-500);
  }

  /* Checked/indeterminate + focus */
  .checkbox.checkbox--checked:not(.checkbox--disabled) .checkbox__input:focus-visible ~ .checkbox__control,
  .checkbox.checkbox--indeterminate:not(.checkbox--disabled) .checkbox__input:focus-visible ~ .checkbox__control {
    outline: var(--sl-focus-ring);
    outline-offset: var(--sl-focus-ring-offset);
  }

  /* Disabled */
  .checkbox--disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .checkbox__label {
    display: inline-block;
    color: var(--sl-input-label-color);
    line-height: var(--toggle-size);
    margin-inline-start: 0.5em;
    user-select: none;
  }

  :host([required]) .checkbox__label::after {
    content: var(--sl-input-required-content);
    margin-inline-start: var(--sl-input-required-content-offset);
  }
`,ps=new WeakMap,bs=new WeakMap,fs=new WeakMap,vs=class{constructor(t,e){(this.host=t).addController(this),this.options=ye({form:t=>t.closest("form"),name:t=>t.name,value:t=>t.value,defaultValue:t=>t.defaultValue,disabled:t=>{var e;return null!=(e=t.disabled)&&e},reportValidity:t=>"function"!=typeof t.reportValidity||t.reportValidity(),setValue:(t,e)=>t.value=e},e),this.handleFormData=this.handleFormData.bind(this),this.handleFormSubmit=this.handleFormSubmit.bind(this),this.handleFormReset=this.handleFormReset.bind(this),this.reportFormValidity=this.reportFormValidity.bind(this),this.handleUserInput=this.handleUserInput.bind(this)}hostConnected(){this.form=this.options.form(this.host),this.form&&(ps.has(this.form)?ps.get(this.form).add(this.host):ps.set(this.form,new Set([this.host])),this.form.addEventListener("formdata",this.handleFormData),this.form.addEventListener("submit",this.handleFormSubmit),this.form.addEventListener("reset",this.handleFormReset),fs.has(this.form)||(fs.set(this.form,this.form.reportValidity),this.form.reportValidity=()=>this.reportFormValidity())),this.host.addEventListener("sl-input",this.handleUserInput)}hostDisconnected(){var t;this.form&&(null==(t=ps.get(this.form))||t.delete(this.host),this.form.removeEventListener("formdata",this.handleFormData),this.form.removeEventListener("submit",this.handleFormSubmit),this.form.removeEventListener("reset",this.handleFormReset),fs.has(this.form)&&(this.form.reportValidity=fs.get(this.form),fs.delete(this.form)),this.form=void 0),this.host.removeEventListener("sl-input",this.handleUserInput)}hostUpdated(){var t;const e=this.host,i=Boolean(bs.get(e)),o=Boolean(e.invalid),s=Boolean(e.required);(null==(t=this.form)?void 0:t.noValidate)?(e.removeAttribute("data-required"),e.removeAttribute("data-optional"),e.removeAttribute("data-invalid"),e.removeAttribute("data-valid"),e.removeAttribute("data-user-invalid"),e.removeAttribute("data-user-valid")):(e.toggleAttribute("data-required",s),e.toggleAttribute("data-optional",!s),e.toggleAttribute("data-invalid",o),e.toggleAttribute("data-valid",!o),e.toggleAttribute("data-user-invalid",o&&i),e.toggleAttribute("data-user-valid",!o&&i))}handleFormData(t){const e=this.options.disabled(this.host),i=this.options.name(this.host),o=this.options.value(this.host),s="sl-button"===this.host.tagName.toLowerCase();!e&&!s&&"string"==typeof i&&i.length>0&&void 0!==o&&(Array.isArray(o)?o.forEach((e=>{t.formData.append(i,e.toString())})):t.formData.append(i,o.toString()))}handleFormSubmit(t){var e;const i=this.options.disabled(this.host),o=this.options.reportValidity;this.form&&!this.form.noValidate&&(null==(e=ps.get(this.form))||e.forEach((t=>{this.setUserInteracted(t,!0)}))),!this.form||this.form.noValidate||i||o(this.host)||(t.preventDefault(),t.stopImmediatePropagation())}handleFormReset(){this.options.setValue(this.host,this.options.defaultValue(this.host)),this.setUserInteracted(this.host,!1)}async handleUserInput(){await this.host.updateComplete,this.setUserInteracted(this.host,!0)}reportFormValidity(){if(this.form&&!this.form.noValidate){const t=this.form.querySelectorAll("*");for(const e of t)if("function"==typeof e.reportValidity&&!e.reportValidity())return!1}return!0}setUserInteracted(t,e){bs.set(t,e),t.requestUpdate()}doAction(t,e){if(this.form){const i=document.createElement("button");i.type=t,i.style.position="absolute",i.style.width="0",i.style.height="0",i.style.clipPath="inset(50%)",i.style.overflow="hidden",i.style.whiteSpace="nowrap",e&&(i.name=e.name,i.value=e.value,["formaction","formenctype","formmethod","formnovalidate","formtarget"].forEach((t=>{e.hasAttribute(t)&&i.setAttribute(t,e.getAttribute(t))}))),this.form.append(i),i.click(),i.remove()}}reset(t){this.doAction("reset",t)}submit(t){this.doAction("submit",t)}},ms=class extends ze{constructor(){super(...arguments),this.formSubmitController=new vs(this,{value:t=>t.checked?t.value||"on":void 0,defaultValue:t=>t.defaultChecked,setValue:(t,e)=>t.checked=e}),this.hasFocus=!1,this.invalid=!1,this.title="",this.name="",this.size="medium",this.disabled=!1,this.required=!1,this.checked=!1,this.indeterminate=!1,this.defaultChecked=!1}firstUpdated(){this.invalid=!this.checkValidity()}handleClick(){this.checked=!this.checked,this.indeterminate=!1,this.emit("sl-change")}handleBlur(){this.hasFocus=!1,this.emit("sl-blur")}handleInput(){this.emit("sl-input")}handleFocus(){this.hasFocus=!0,this.emit("sl-focus")}handleDisabledChange(){this.input.disabled=this.disabled,this.invalid=!this.checkValidity()}handleStateChange(){this.input.checked=this.checked,this.input.indeterminate=this.indeterminate,this.invalid=!this.checkValidity()}click(){this.input.click()}focus(t){this.input.focus(t)}blur(){this.input.blur()}checkValidity(){return this.input.checkValidity()}reportValidity(){return this.input.reportValidity()}setCustomValidity(t){this.input.setCustomValidity(t),this.invalid=!this.checkValidity()}render(){return Ht`
      <label
        part="base"
        class=${li({checkbox:!0,"checkbox--checked":this.checked,"checkbox--disabled":this.disabled,"checkbox--focused":this.hasFocus,"checkbox--indeterminate":this.indeterminate,"checkbox--small":"small"===this.size,"checkbox--medium":"medium"===this.size,"checkbox--large":"large"===this.size})}
      >
        <input
          class="checkbox__input"
          type="checkbox"
          title=${this.title}
          name=${this.name}
          value=${ri(this.value)}
          .indeterminate=${ns(this.indeterminate)}
          .checked=${ns(this.checked)}
          .disabled=${this.disabled}
          .required=${this.required}
          aria-checked=${this.checked?"true":"false"}
          @click=${this.handleClick}
          @input=${this.handleInput}
          @blur=${this.handleBlur}
          @focus=${this.handleFocus}
        />

        <span
          part="control${this.checked?" control--checked":""}${this.indeterminate?" control--indeterminate":""}"
          class="checkbox__control"
        >
          ${this.checked?Ht`
                <sl-icon part="checked-icon" class="checkbox__checked-icon" library="system" name="check"></sl-icon>
              `:""}
          ${!this.checked&&this.indeterminate?Ht`
                <sl-icon
                  part="indeterminate-icon"
                  class="checkbox__indeterminate-icon"
                  library="system"
                  name="indeterminate"
                ></sl-icon>
              `:""}
        </span>

        <slot part="label" class="checkbox__label"></slot>
      </label>
    `}};ms.styles=us,$e([Te('input[type="checkbox"]')],ms.prototype,"input",2),$e([Ee()],ms.prototype,"hasFocus",2),$e([Ee()],ms.prototype,"invalid",2),$e([Ce()],ms.prototype,"title",2),$e([Ce()],ms.prototype,"name",2),$e([Ce()],ms.prototype,"value",2),$e([Ce({reflect:!0})],ms.prototype,"size",2),$e([Ce({type:Boolean,reflect:!0})],ms.prototype,"disabled",2),$e([Ce({type:Boolean,reflect:!0})],ms.prototype,"required",2),$e([Ce({type:Boolean,reflect:!0})],ms.prototype,"checked",2),$e([Ce({type:Boolean,reflect:!0})],ms.prototype,"indeterminate",2),$e([((t="value")=>(e,i)=>{const o=e.constructor,s=o.prototype.attributeChangedCallback;o.prototype.attributeChangedCallback=function(e,r,n){var a;const l=o.getPropertyOptions(t);if(e===("string"==typeof l.attribute?l.attribute:t)){const e=l.converter||mt,o=("function"==typeof e?e:null!=(a=null==e?void 0:e.fromAttribute)?a:mt.fromAttribute)(n,l.type);this[t]!==o&&(this[i]=o)}s.call(this,e,r,n)}})("checked")],ms.prototype,"defaultChecked",2),$e([xe("disabled",{waitUntilFirstUpdate:!0})],ms.prototype,"handleDisabledChange",1),$e([xe("checked",{waitUntilFirstUpdate:!0}),xe("indeterminate",{waitUntilFirstUpdate:!0})],ms.prototype,"handleStateChange",1),ms=$e([ke("sl-checkbox")],ms);var gs=ht`
  ${de}

  :host {
    --track-width: 2px;
    --track-color: rgb(128 128 128 / 25%);
    --indicator-color: var(--sl-color-primary-600);
    --speed: 2s;

    display: inline-flex;
    width: 1em;
    height: 1em;
  }

  .spinner {
    flex: 1 1 auto;
    height: 100%;
    width: 100%;
  }

  .spinner__track,
  .spinner__indicator {
    fill: none;
    stroke-width: var(--track-width);
    r: calc(0.5em - var(--track-width) / 2);
    cx: 0.5em;
    cy: 0.5em;
    transform-origin: 50% 50%;
  }

  .spinner__track {
    stroke: var(--track-color);
    transform-origin: 0% 0%;
    mix-blend-mode: multiply;
  }

  .spinner__indicator {
    stroke: var(--indicator-color);
    stroke-linecap: round;
    stroke-dasharray: 150% 75%;
    animation: spin var(--speed) linear infinite;
  }

  @keyframes spin {
    0% {
      rotate: 0deg;
      stroke-dasharray: 0.01em, 2.75em;
    }

    50% {
      rotate: 450deg;
      stroke-dasharray: 1.375em, 1.375em;
    }

    100% {
      rotate: 1080deg;
      stroke-dasharray: 0.01em, 2.75em;
    }
  }
`,ys=class extends ze{constructor(){super(...arguments),this.localize=new oi(this)}render(){return Ht`
      <svg part="base" class="spinner" role="progressbar" aria-valuetext=${this.localize.term("loading")}>
        <circle class="spinner__track"></circle>
        <circle class="spinner__indicator"></circle>
      </svg>
    `}};ys.styles=gs,ys=$e([ke("sl-spinner")],ys);var ws=ht`
  ${de}

  :host {
    --divider-width: 4px;
    --divider-hit-area: 12px;
    --min: 0%;
    --max: 100%;

    display: grid;
  }

  .start,
  .end {
    overflow: hidden;
  }

  .divider {
    flex: 0 0 var(--divider-width);
    display: flex;
    position: relative;
    align-items: center;
    justify-content: center;
    background-color: var(--sl-color-neutral-200);
    color: var(--sl-color-neutral-900);
    z-index: 1;
  }

  .divider:focus {
    outline: none;
  }

  :host(:not([disabled])) .divider:focus-visible {
    background-color: var(--sl-color-primary-600);
    color: var(--sl-color-neutral-0);
  }

  :host([disabled]) .divider {
    cursor: not-allowed;
  }

  /* Horizontal */
  :host(:not([vertical], [disabled])) .divider {
    cursor: col-resize;
  }

  :host(:not([vertical])) .divider::after {
    display: flex;
    content: '';
    position: absolute;
    height: 100%;
    left: calc(var(--divider-hit-area) / -2 + var(--divider-width) / 2);
    width: var(--divider-hit-area);
  }

  /* Vertical */
  :host([vertical]) {
    flex-direction: column;
  }

  :host([vertical]:not([disabled])) .divider {
    cursor: row-resize;
  }

  :host([vertical]) .divider::after {
    content: '';
    position: absolute;
    width: 100%;
    top: calc(var(--divider-hit-area) / -2 + var(--divider-width) / 2);
    height: var(--divider-hit-area);
  }

  @media (forced-colors: active) {
    .divider {
      outline: solid 1px transparent;
    }
  }
`,_s=class extends ze{constructor(){super(...arguments),this.localize=new oi(this),this.position=50,this.vertical=!1,this.disabled=!1,this.snapThreshold=12}connectedCallback(){super.connectedCallback(),this.resizeObserver=new ResizeObserver((t=>this.handleResize(t))),this.updateComplete.then((()=>this.resizeObserver.observe(this))),this.detectSize(),this.cachedPositionInPixels=this.percentageToPixels(this.position)}disconnectedCallback(){super.disconnectedCallback(),this.resizeObserver.unobserve(this)}detectSize(){const{width:t,height:e}=this.getBoundingClientRect();this.size=this.vertical?e:t}percentageToPixels(t){return this.size*(t/100)}pixelsToPercentage(t){return t/this.size*100}handleDrag(t){const e="rtl"===this.localize.dir();this.disabled||(t.cancelable&&t.preventDefault(),function(t,e){function i(i){const o=t.getBoundingClientRect(),s=t.ownerDocument.defaultView,r=o.left+s.pageXOffset,n=o.top+s.pageYOffset,a=i.pageX-r,l=i.pageY-n;(null==e?void 0:e.onMove)&&e.onMove(a,l)}document.addEventListener("pointermove",i,{passive:!0}),document.addEventListener("pointerup",(function t(){document.removeEventListener("pointermove",i),document.removeEventListener("pointerup",t),(null==e?void 0:e.onStop)&&e.onStop()})),(null==e?void 0:e.initialEvent)instanceof PointerEvent&&i(e.initialEvent)}(this,{onMove:(t,i)=>{let o=this.vertical?i:t;"end"===this.primary&&(o=this.size-o),this.snap&&this.snap.split(" ").forEach((t=>{let i;i=t.endsWith("%")?this.size*(parseFloat(t)/100):parseFloat(t),e&&!this.vertical&&(i=this.size-i),o>=i-this.snapThreshold&&o<=i+this.snapThreshold&&(o=i)})),this.position=ds(this.pixelsToPercentage(o),0,100)},initialEvent:t}))}handleKeyDown(t){if(!this.disabled&&["ArrowLeft","ArrowRight","ArrowUp","ArrowDown","Home","End"].includes(t.key)){let e=this.position;const i=(t.shiftKey?10:1)*("end"===this.primary?-1:1);t.preventDefault(),("ArrowLeft"===t.key&&!this.vertical||"ArrowUp"===t.key&&this.vertical)&&(e-=i),("ArrowRight"===t.key&&!this.vertical||"ArrowDown"===t.key&&this.vertical)&&(e+=i),"Home"===t.key&&(e="end"===this.primary?100:0),"End"===t.key&&(e="end"===this.primary?0:100),this.position=ds(e,0,100)}}handleResize(t){const{width:e,height:i}=t[0].contentRect;this.size=this.vertical?i:e,this.primary&&(this.position=this.pixelsToPercentage(this.cachedPositionInPixels))}handlePositionChange(){this.cachedPositionInPixels=this.percentageToPixels(this.position),this.positionInPixels=this.percentageToPixels(this.position),this.emit("sl-reposition")}handlePositionInPixelsChange(){this.position=this.pixelsToPercentage(this.positionInPixels)}handleVerticalChange(){this.detectSize()}render(){const t=this.vertical?"gridTemplateRows":"gridTemplateColumns",e=this.vertical?"gridTemplateColumns":"gridTemplateRows",i="rtl"===this.localize.dir(),o=`\n      clamp(\n        0%,\n        clamp(\n          var(--min),\n          ${this.position}% - var(--divider-width) / 2,\n          var(--max)\n        ),\n        calc(100% - var(--divider-width))\n      )\n    `,s="auto";return"end"===this.primary?i&&!this.vertical?this.style[t]=`${o} var(--divider-width) ${s}`:this.style[t]=`${s} var(--divider-width) ${o}`:i&&!this.vertical?this.style[t]=`${s} var(--divider-width) ${o}`:this.style[t]=`${o} var(--divider-width) ${s}`,this.style[e]="",Ht`
      <slot name="start" part="panel start" class="start"></slot>

      <slot
        name="divider"
        part="divider"
        class="divider"
        tabindex=${ri(this.disabled?void 0:"0")}
        role="separator"
        aria-label=${this.localize.term("resize")}
        @keydown=${this.handleKeyDown}
        @mousedown=${this.handleDrag}
        @touchstart=${this.handleDrag}
      ></slot>

      <slot name="end" part="panel end" class="end"></slot>
    `}};_s.styles=ws,$e([Te(".divider")],_s.prototype,"divider",2),$e([Ce({type:Number,reflect:!0})],_s.prototype,"position",2),$e([Ce({attribute:"position-in-pixels",type:Number})],_s.prototype,"positionInPixels",2),$e([Ce({type:Boolean,reflect:!0})],_s.prototype,"vertical",2),$e([Ce({type:Boolean,reflect:!0})],_s.prototype,"disabled",2),$e([Ce()],_s.prototype,"primary",2),$e([Ce()],_s.prototype,"snap",2),$e([Ce({type:Number,attribute:"snap-threshold"})],_s.prototype,"snapThreshold",2),$e([xe("position")],_s.prototype,"handlePositionChange",1),$e([xe("positionInPixels")],_s.prototype,"handlePositionInPixelsChange",1),$e([xe("vertical")],_s.prototype,"handleVerticalChange",1),_s=$e([ke("sl-split-panel")],_s);var $s=ht`
  ${de}

  :host {
    display: inline-block;
    position: relative;
    width: auto;
    cursor: pointer;
  }

  .button {
    display: inline-flex;
    align-items: stretch;
    justify-content: center;
    width: 100%;
    border-style: solid;
    border-width: var(--sl-input-border-width);
    font-family: var(--sl-input-font-family);
    font-weight: var(--sl-font-weight-semibold);
    text-decoration: none;
    user-select: none;
    white-space: nowrap;
    vertical-align: middle;
    padding: 0;
    transition: var(--sl-transition-x-fast) background-color, var(--sl-transition-x-fast) color,
      var(--sl-transition-x-fast) border, var(--sl-transition-x-fast) box-shadow;
    cursor: inherit;
  }

  .button::-moz-focus-inner {
    border: 0;
  }

  .button:focus {
    outline: none;
  }

  .button:focus-visible {
    outline: var(--sl-focus-ring);
    outline-offset: var(--sl-focus-ring-offset);
  }

  .button--disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* When disabled, prevent mouse events from bubbling up */
  .button--disabled * {
    pointer-events: none;
  }

  .button__prefix,
  .button__suffix {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    pointer-events: none;
  }

  .button__label {
    display: inline-block;
  }

  .button__label::slotted(sl-icon) {
    vertical-align: -2px;
  }

  /*
   * Standard buttons
   */

  /* Default */
  .button--standard.button--default {
    background-color: var(--sl-color-neutral-0);
    border-color: var(--sl-color-neutral-300);
    color: var(--sl-color-neutral-700);
  }

  .button--standard.button--default:hover:not(.button--disabled) {
    background-color: var(--sl-color-primary-50);
    border-color: var(--sl-color-primary-300);
    color: var(--sl-color-primary-700);
  }

  .button--standard.button--default:active:not(.button--disabled) {
    background-color: var(--sl-color-primary-100);
    border-color: var(--sl-color-primary-400);
    color: var(--sl-color-primary-700);
  }

  /* Primary */
  .button--standard.button--primary {
    background-color: var(--sl-color-primary-600);
    border-color: var(--sl-color-primary-600);
    color: var(--sl-color-neutral-0);
  }

  .button--standard.button--primary:hover:not(.button--disabled) {
    background-color: var(--sl-color-primary-500);
    border-color: var(--sl-color-primary-500);
    color: var(--sl-color-neutral-0);
  }

  .button--standard.button--primary:active:not(.button--disabled) {
    background-color: var(--sl-color-primary-600);
    border-color: var(--sl-color-primary-600);
    color: var(--sl-color-neutral-0);
  }

  /* Success */
  .button--standard.button--success {
    background-color: var(--sl-color-success-600);
    border-color: var(--sl-color-success-600);
    color: var(--sl-color-neutral-0);
  }

  .button--standard.button--success:hover:not(.button--disabled) {
    background-color: var(--sl-color-success-500);
    border-color: var(--sl-color-success-500);
    color: var(--sl-color-neutral-0);
  }

  .button--standard.button--success:active:not(.button--disabled) {
    background-color: var(--sl-color-success-600);
    border-color: var(--sl-color-success-600);
    color: var(--sl-color-neutral-0);
  }

  /* Neutral */
  .button--standard.button--neutral {
    background-color: var(--sl-color-neutral-600);
    border-color: var(--sl-color-neutral-600);
    color: var(--sl-color-neutral-0);
  }

  .button--standard.button--neutral:hover:not(.button--disabled) {
    background-color: var(--sl-color-neutral-500);
    border-color: var(--sl-color-neutral-500);
    color: var(--sl-color-neutral-0);
  }

  .button--standard.button--neutral:active:not(.button--disabled) {
    background-color: var(--sl-color-neutral-600);
    border-color: var(--sl-color-neutral-600);
    color: var(--sl-color-neutral-0);
  }

  /* Warning */
  .button--standard.button--warning {
    background-color: var(--sl-color-warning-600);
    border-color: var(--sl-color-warning-600);
    color: var(--sl-color-neutral-0);
  }
  .button--standard.button--warning:hover:not(.button--disabled) {
    background-color: var(--sl-color-warning-500);
    border-color: var(--sl-color-warning-500);
    color: var(--sl-color-neutral-0);
  }

  .button--standard.button--warning:active:not(.button--disabled) {
    background-color: var(--sl-color-warning-600);
    border-color: var(--sl-color-warning-600);
    color: var(--sl-color-neutral-0);
  }

  /* Danger */
  .button--standard.button--danger {
    background-color: var(--sl-color-danger-600);
    border-color: var(--sl-color-danger-600);
    color: var(--sl-color-neutral-0);
  }

  .button--standard.button--danger:hover:not(.button--disabled) {
    background-color: var(--sl-color-danger-500);
    border-color: var(--sl-color-danger-500);
    color: var(--sl-color-neutral-0);
  }

  .button--standard.button--danger:active:not(.button--disabled) {
    background-color: var(--sl-color-danger-600);
    border-color: var(--sl-color-danger-600);
    color: var(--sl-color-neutral-0);
  }

  /*
   * Outline buttons
   */

  .button--outline {
    background: none;
    border: solid 1px;
  }

  /* Default */
  .button--outline.button--default {
    border-color: var(--sl-color-neutral-300);
    color: var(--sl-color-neutral-700);
  }

  .button--outline.button--default:hover:not(.button--disabled),
  .button--outline.button--default.button--checked:not(.button--disabled) {
    border-color: var(--sl-color-primary-600);
    background-color: var(--sl-color-primary-600);
    color: var(--sl-color-neutral-0);
  }

  .button--outline.button--default:active:not(.button--disabled) {
    border-color: var(--sl-color-primary-700);
    background-color: var(--sl-color-primary-700);
    color: var(--sl-color-neutral-0);
  }

  /* Primary */
  .button--outline.button--primary {
    border-color: var(--sl-color-primary-600);
    color: var(--sl-color-primary-600);
  }

  .button--outline.button--primary:hover:not(.button--disabled),
  .button--outline.button--primary.button--checked:not(.button--disabled) {
    background-color: var(--sl-color-primary-600);
    color: var(--sl-color-neutral-0);
  }

  .button--outline.button--primary:active:not(.button--disabled) {
    border-color: var(--sl-color-primary-700);
    background-color: var(--sl-color-primary-700);
    color: var(--sl-color-neutral-0);
  }

  /* Success */
  .button--outline.button--success {
    border-color: var(--sl-color-success-600);
    color: var(--sl-color-success-600);
  }

  .button--outline.button--success:hover:not(.button--disabled),
  .button--outline.button--success.button--checked:not(.button--disabled) {
    background-color: var(--sl-color-success-600);
    color: var(--sl-color-neutral-0);
  }

  .button--outline.button--success:active:not(.button--disabled) {
    border-color: var(--sl-color-success-700);
    background-color: var(--sl-color-success-700);
    color: var(--sl-color-neutral-0);
  }

  /* Neutral */
  .button--outline.button--neutral {
    border-color: var(--sl-color-neutral-600);
    color: var(--sl-color-neutral-600);
  }

  .button--outline.button--neutral:hover:not(.button--disabled),
  .button--outline.button--neutral.button--checked:not(.button--disabled) {
    background-color: var(--sl-color-neutral-600);
    color: var(--sl-color-neutral-0);
  }

  .button--outline.button--neutral:active:not(.button--disabled) {
    border-color: var(--sl-color-neutral-700);
    background-color: var(--sl-color-neutral-700);
    color: var(--sl-color-neutral-0);
  }

  /* Warning */
  .button--outline.button--warning {
    border-color: var(--sl-color-warning-600);
    color: var(--sl-color-warning-600);
  }

  .button--outline.button--warning:hover:not(.button--disabled),
  .button--outline.button--warning.button--checked:not(.button--disabled) {
    background-color: var(--sl-color-warning-600);
    color: var(--sl-color-neutral-0);
  }

  .button--outline.button--warning:active:not(.button--disabled) {
    border-color: var(--sl-color-warning-700);
    background-color: var(--sl-color-warning-700);
    color: var(--sl-color-neutral-0);
  }

  /* Danger */
  .button--outline.button--danger {
    border-color: var(--sl-color-danger-600);
    color: var(--sl-color-danger-600);
  }

  .button--outline.button--danger:hover:not(.button--disabled),
  .button--outline.button--danger.button--checked:not(.button--disabled) {
    background-color: var(--sl-color-danger-600);
    color: var(--sl-color-neutral-0);
  }

  .button--outline.button--danger:active:not(.button--disabled) {
    border-color: var(--sl-color-danger-700);
    background-color: var(--sl-color-danger-700);
    color: var(--sl-color-neutral-0);
  }

  @media (forced-colors: active) {
    .button.button--outline.button--checked:not(.button--disabled) {
      outline: solid 2px transparent;
    }
  }

  /*
   * Text buttons
   */

  .button--text {
    background-color: transparent;
    border-color: transparent;
    color: var(--sl-color-primary-600);
  }

  .button--text:hover:not(.button--disabled) {
    background-color: transparent;
    border-color: transparent;
    color: var(--sl-color-primary-500);
  }

  .button--text:focus-visible:not(.button--disabled) {
    background-color: transparent;
    border-color: transparent;
    color: var(--sl-color-primary-500);
  }

  .button--text:active:not(.button--disabled) {
    background-color: transparent;
    border-color: transparent;
    color: var(--sl-color-primary-700);
  }

  /*
   * Size modifiers
   */

  .button--small {
    font-size: var(--sl-button-font-size-small);
    height: var(--sl-input-height-small);
    line-height: calc(var(--sl-input-height-small) - var(--sl-input-border-width) * 2);
    border-radius: var(--sl-input-border-radius-small);
  }

  .button--medium {
    font-size: var(--sl-button-font-size-medium);
    height: var(--sl-input-height-medium);
    line-height: calc(var(--sl-input-height-medium) - var(--sl-input-border-width) * 2);
    border-radius: var(--sl-input-border-radius-medium);
  }

  .button--large {
    font-size: var(--sl-button-font-size-large);
    height: var(--sl-input-height-large);
    line-height: calc(var(--sl-input-height-large) - var(--sl-input-border-width) * 2);
    border-radius: var(--sl-input-border-radius-large);
  }

  /*
   * Pill modifier
   */

  .button--pill.button--small {
    border-radius: var(--sl-input-height-small);
  }

  .button--pill.button--medium {
    border-radius: var(--sl-input-height-medium);
  }

  .button--pill.button--large {
    border-radius: var(--sl-input-height-large);
  }

  /*
   * Circle modifier
   */

  .button--circle {
    padding-left: 0;
    padding-right: 0;
  }

  .button--circle.button--small {
    width: var(--sl-input-height-small);
    border-radius: 50%;
  }

  .button--circle.button--medium {
    width: var(--sl-input-height-medium);
    border-radius: 50%;
  }

  .button--circle.button--large {
    width: var(--sl-input-height-large);
    border-radius: 50%;
  }

  .button--circle .button__prefix,
  .button--circle .button__suffix,
  .button--circle .button__caret {
    display: none;
  }

  /*
   * Caret modifier
   */

  .button--caret .button__suffix {
    display: none;
  }

  .button--caret .button__caret {
    height: auto;
  }

  /*
   * Loading modifier
   */

  .button--loading {
    position: relative;
    cursor: wait;
  }

  .button--loading .button__prefix,
  .button--loading .button__label,
  .button--loading .button__suffix,
  .button--loading .button__caret {
    visibility: hidden;
  }

  .button--loading sl-spinner {
    --indicator-color: currentColor;
    position: absolute;
    font-size: 1em;
    height: 1em;
    width: 1em;
    top: calc(50% - 0.5em);
    left: calc(50% - 0.5em);
  }

  /*
   * Badges
   */

  .button ::slotted(sl-badge) {
    position: absolute;
    top: 0;
    right: 0;
    translate: 50% -50%;
    pointer-events: none;
  }

  .button--rtl ::slotted(sl-badge) {
    right: auto;
    left: 0;
    translate: -50% -50%;
  }

  /*
   * Button spacing
   */

  .button--has-label.button--small .button__label {
    padding: 0 var(--sl-spacing-small);
  }

  .button--has-label.button--medium .button__label {
    padding: 0 var(--sl-spacing-medium);
  }

  .button--has-label.button--large .button__label {
    padding: 0 var(--sl-spacing-large);
  }

  .button--has-prefix.button--small {
    padding-inline-start: var(--sl-spacing-x-small);
  }

  .button--has-prefix.button--small .button__label {
    padding-inline-start: var(--sl-spacing-x-small);
  }

  .button--has-prefix.button--medium {
    padding-inline-start: var(--sl-spacing-small);
  }

  .button--has-prefix.button--medium .button__label {
    padding-inline-start: var(--sl-spacing-small);
  }

  .button--has-prefix.button--large {
    padding-inline-start: var(--sl-spacing-small);
  }

  .button--has-prefix.button--large .button__label {
    padding-inline-start: var(--sl-spacing-small);
  }

  .button--has-suffix.button--small,
  .button--caret.button--small {
    padding-inline-end: var(--sl-spacing-x-small);
  }

  .button--has-suffix.button--small .button__label,
  .button--caret.button--small .button__label {
    padding-inline-end: var(--sl-spacing-x-small);
  }

  .button--has-suffix.button--medium,
  .button--caret.button--medium {
    padding-inline-end: var(--sl-spacing-small);
  }

  .button--has-suffix.button--medium .button__label,
  .button--caret.button--medium .button__label {
    padding-inline-end: var(--sl-spacing-small);
  }

  .button--has-suffix.button--large,
  .button--caret.button--large {
    padding-inline-end: var(--sl-spacing-small);
  }

  .button--has-suffix.button--large .button__label,
  .button--caret.button--large .button__label {
    padding-inline-end: var(--sl-spacing-small);
  }

  /*
   * Button groups support a variety of button types (e.g. buttons with tooltips, buttons as dropdown triggers, etc.).
   * This means buttons aren't always direct descendants of the button group, thus we can't target them with the
   * ::slotted selector. To work around this, the button group component does some magic to add these special classes to
   * buttons and we style them here instead.
   */

  :host(.sl-button-group__button--first:not(.sl-button-group__button--last)) .button {
    border-start-end-radius: 0;
    border-end-end-radius: 0;
  }

  :host(.sl-button-group__button--inner) .button {
    border-radius: 0;
  }

  :host(.sl-button-group__button--last:not(.sl-button-group__button--first)) .button {
    border-start-start-radius: 0;
    border-end-start-radius: 0;
  }

  /* All except the first */
  :host(.sl-button-group__button:not(.sl-button-group__button--first)) {
    margin-inline-start: calc(-1 * var(--sl-input-border-width));
  }

  /* Add a visual separator between solid buttons */
  :host(.sl-button-group__button:not(.sl-button-group__button--first, .sl-button-group__button--radio, [variant='default']):not(:hover))
    .button:after {
    content: '';
    position: absolute;
    top: 0;
    inset-inline-start: 0;
    bottom: 0;
    border-left: solid 1px rgb(128 128 128 / 33%);
    mix-blend-mode: multiply;
  }

  /* Bump hovered, focused, and checked buttons up so their focus ring isn't clipped */
  :host(.sl-button-group__button--hover) {
    z-index: 1;
  }

  /* Focus and checked are always on top */
  :host(.sl-button-group__button--focus),
  :host(.sl-button-group__button[checked]) {
    z-index: 2;
  }
`,xs=class extends ze{constructor(){super(...arguments),this.formSubmitController=new vs(this,{form:t=>{if(t.hasAttribute("form")){const e=t.getRootNode(),i=t.getAttribute("form");return e.getElementById(i)}return t.closest("form")}}),this.hasSlotController=new si(this,"[default]","prefix","suffix"),this.localize=new oi(this),this.hasFocus=!1,this.invalid=!1,this.title="",this.variant="default",this.size="medium",this.caret=!1,this.disabled=!1,this.loading=!1,this.outline=!1,this.pill=!1,this.circle=!1,this.type="button",this.name="",this.value="",this.href=""}firstUpdated(){this.isButton()&&(this.invalid=!this.button.checkValidity())}handleBlur(){this.hasFocus=!1,this.emit("sl-blur")}handleFocus(){this.hasFocus=!0,this.emit("sl-focus")}handleClick(t){if(this.disabled||this.loading)return t.preventDefault(),void t.stopPropagation();"submit"===this.type&&this.formSubmitController.submit(this),"reset"===this.type&&this.formSubmitController.reset(this)}isButton(){return!this.href}isLink(){return!!this.href}handleDisabledChange(){this.isButton()&&(this.button.disabled=this.disabled,this.invalid=!this.button.checkValidity())}click(){this.button.click()}focus(t){this.button.focus(t)}blur(){this.button.blur()}checkValidity(){return!this.isButton()||this.button.checkValidity()}reportValidity(){return!this.isButton()||this.button.reportValidity()}setCustomValidity(t){this.isButton()&&(this.button.setCustomValidity(t),this.invalid=!this.button.checkValidity())}render(){const t=this.isLink(),e=t?pi`a`:pi`button`;return vi`
      <${e}
        part="base"
        class=${li({button:!0,"button--default":"default"===this.variant,"button--primary":"primary"===this.variant,"button--success":"success"===this.variant,"button--neutral":"neutral"===this.variant,"button--warning":"warning"===this.variant,"button--danger":"danger"===this.variant,"button--text":"text"===this.variant,"button--small":"small"===this.size,"button--medium":"medium"===this.size,"button--large":"large"===this.size,"button--caret":this.caret,"button--circle":this.circle,"button--disabled":this.disabled,"button--focused":this.hasFocus,"button--loading":this.loading,"button--standard":!this.outline,"button--outline":this.outline,"button--pill":this.pill,"button--rtl":"rtl"===this.localize.dir(),"button--has-label":this.hasSlotController.test("[default]"),"button--has-prefix":this.hasSlotController.test("prefix"),"button--has-suffix":this.hasSlotController.test("suffix")})}
        ?disabled=${ri(t?void 0:this.disabled)}
        type=${ri(t?void 0:this.type)}
        title=${this.title}
        name=${ri(t?void 0:this.name)}
        value=${ri(t?void 0:this.value)}
        href=${ri(t?this.href:void 0)}
        target=${ri(t?this.target:void 0)}
        download=${ri(t?this.download:void 0)}
        rel=${ri(t&&this.target?"noreferrer noopener":void 0)}
        role=${ri(t?void 0:"button")}
        aria-disabled=${this.disabled?"true":"false"}
        tabindex=${this.disabled?"-1":"0"}
        @blur=${this.handleBlur}
        @focus=${this.handleFocus}
        @click=${this.handleClick}
      >
        <slot name="prefix" part="prefix" class="button__prefix"></slot>
        <slot part="label" class="button__label"></slot>
        <slot name="suffix" part="suffix" class="button__suffix"></slot>
        ${this.caret?vi` <sl-icon part="caret" class="button__caret" library="system" name="caret"></sl-icon> `:""}
        ${this.loading?vi`<sl-spinner></sl-spinner>`:""}
      </${e}>
    `}};xs.styles=$s,$e([Te(".button")],xs.prototype,"button",2),$e([Ee()],xs.prototype,"hasFocus",2),$e([Ee()],xs.prototype,"invalid",2),$e([Ce()],xs.prototype,"title",2),$e([Ce({reflect:!0})],xs.prototype,"variant",2),$e([Ce({reflect:!0})],xs.prototype,"size",2),$e([Ce({type:Boolean,reflect:!0})],xs.prototype,"caret",2),$e([Ce({type:Boolean,reflect:!0})],xs.prototype,"disabled",2),$e([Ce({type:Boolean,reflect:!0})],xs.prototype,"loading",2),$e([Ce({type:Boolean,reflect:!0})],xs.prototype,"outline",2),$e([Ce({type:Boolean,reflect:!0})],xs.prototype,"pill",2),$e([Ce({type:Boolean,reflect:!0})],xs.prototype,"circle",2),$e([Ce()],xs.prototype,"type",2),$e([Ce()],xs.prototype,"name",2),$e([Ce()],xs.prototype,"value",2),$e([Ce()],xs.prototype,"href",2),$e([Ce()],xs.prototype,"target",2),$e([Ce()],xs.prototype,"download",2),$e([Ce()],xs.prototype,"form",2),$e([Ce({attribute:"formaction"})],xs.prototype,"formAction",2),$e([Ce({attribute:"formenctype"})],xs.prototype,"formEnctype",2),$e([Ce({attribute:"formmethod"})],xs.prototype,"formMethod",2),$e([Ce({attribute:"formnovalidate",type:Boolean})],xs.prototype,"formNoValidate",2),$e([Ce({attribute:"formtarget"})],xs.prototype,"formTarget",2),$e([xe("disabled",{waitUntilFirstUpdate:!0})],xs.prototype,"handleDisabledChange",1),xs=$e([ke("sl-button")],xs);class ks extends it{static styles=r`
        .loading {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 5% 0%;
            font-size: 15vw;
            height: 85vh;
        }

        sl-dialog {
            --width: 100vw;
            --header-spacing: var(--sl-spacing-small);
            --body-spacing: var(--sl-spacing-2x-small);
        }

        .dialog-overview::part(panel) {
            height: 95vh;
            overflow: hidden;
            display: block;
        }

        .plot-iframe {
            height: 0%;
            width: 100%;
        }
    `;static properties={path:{type:String},_dialogOpened:{type:Boolean,state:!0},_visible:{type:Boolean,state:!0}};connectedCallback(){super.connectedCallback(),this.observer=new IntersectionObserver(((t,e)=>{t.forEach((t=>{t.isIntersecting?this._visible=!0:this._visible=!1}))})),this.observer.observe(this.parentElement)}disconnectedCallback(){super.disconnectedCallback(),this.observer.disconnect()}constructor(){super(),this._visible=!1,this._dialogOpened=!1}hideLoading(t,e){this.renderRoot.querySelector(`#${t}`).remove(),this.renderRoot.querySelector(`#${e}`).style.height="85vh"}openFullscreen(){const t=this.renderRoot.querySelector(".dialog-overview");if(!t)throw Error("failed to find dialog element, unable to open fullscreen diagram view.");return this._dialogOpened=!0,t.show()}spinnerTemplate(t){return R`
            <div id=${t} class="loading">
                <sl-spinner></sl-spinner>
            </div>
        `}iframeTemplate(t,e){return R`
            ${this.spinnerTemplate(t)}
            <iframe id=${e} seamless frameborder="0" scrolling="no" class="plot-iframe"
                @load=${()=>this.hideLoading(t,e)} src=${this.path}>
            </iframe>
        `}dialogTemplate(){return R`
            <sl-dialog class="dialog-overview">
                ${this._dialogOpened?this.iframeTemplate("dialog-spinner","dialog-iframe"):R``}
            </sl-dialog>
        `}render(){return this._visible?R`
            <sl-divider></sl-divider>

            <div style="display: flex;flex-direction: column;align-items: flex-end;">
                ${this.dialogTemplate()}
                <sl-button style="margin-right: 2em;" @click=${this.openFullscreen}>
                    Open Fullscreen View
                </sl-button>
            </div>

            ${this.iframeTemplate("page-spinner","page-iframe")}
        `:R``}}customElements.define("sc-diagram",ks);var As=ht`
  ${de}

  :host {
    display: block;
  }

  .details {
    border: solid 1px var(--sl-color-neutral-200);
    border-radius: var(--sl-border-radius-medium);
    background-color: var(--sl-color-neutral-0);
    overflow-anchor: none;
  }

  .details--disabled {
    opacity: 0.5;
  }

  .details__header {
    display: flex;
    align-items: center;
    border-radius: inherit;
    padding: var(--sl-spacing-medium);
    user-select: none;
    cursor: pointer;
  }

  .details__header:focus {
    outline: none;
  }

  .details__header:focus-visible {
    outline: var(--sl-focus-ring);
    outline-offset: calc(1px + var(--sl-focus-ring-offset));
  }

  .details--disabled .details__header {
    cursor: not-allowed;
  }

  .details--disabled .details__header:focus-visible {
    outline: none;
    box-shadow: none;
  }

  .details__summary {
    flex: 1 1 auto;
    display: flex;
    align-items: center;
  }

  .details__summary-icon {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    transition: var(--sl-transition-medium) rotate ease;
  }

  .details--open .details__summary-icon {
    rotate: 90deg;
  }

  .details--open.details--rtl .details__summary-icon {
    rotate: -90deg;
  }

  .details--open slot[name='expand-icon'],
  .details:not(.details--open) slot[name='collapse-icon'] {
    display: none;
  }

  .details__body {
    overflow: hidden;
  }

  .details__content {
    display: block;
    padding: var(--sl-spacing-medium);
  }
`,Cs=class extends ze{constructor(){super(...arguments),this.localize=new oi(this),this.open=!1,this.disabled=!1}firstUpdated(){this.body.hidden=!this.open,this.body.style.height=this.open?"auto":"0"}handleSummaryClick(){this.disabled||(this.open?this.hide():this.show(),this.header.focus())}handleSummaryKeyDown(t){"Enter"!==t.key&&" "!==t.key||(t.preventDefault(),this.open?this.hide():this.show()),"ArrowUp"!==t.key&&"ArrowLeft"!==t.key||(t.preventDefault(),this.hide()),"ArrowDown"!==t.key&&"ArrowRight"!==t.key||(t.preventDefault(),this.show())}async handleOpenChange(){if(this.open){if(this.emit("sl-show",{cancelable:!0}).defaultPrevented)return void(this.open=!1);await Ne(this.body),this.body.hidden=!1;const{keyframes:t,options:e}=Ye(this,"details.show",{dir:this.localize.dir()});await He(this.body,Ve(t,this.body.scrollHeight),e),this.body.style.height="auto",this.emit("sl-after-show")}else{if(this.emit("sl-hide",{cancelable:!0}).defaultPrevented)return void(this.open=!0);await Ne(this.body);const{keyframes:t,options:e}=Ye(this,"details.hide",{dir:this.localize.dir()});await He(this.body,Ve(t,this.body.scrollHeight),e),this.body.hidden=!0,this.body.style.height="auto",this.emit("sl-after-hide")}}async show(){if(!this.open&&!this.disabled)return this.open=!0,Be(this,"sl-after-show")}async hide(){if(this.open&&!this.disabled)return this.open=!1,Be(this,"sl-after-hide")}render(){const t="rtl"===this.localize.dir();return Ht`
      <div
        part="base"
        class=${li({details:!0,"details--open":this.open,"details--disabled":this.disabled,"details--rtl":t})}
      >
        <header
          part="header"
          id="header"
          class="details__header"
          role="button"
          aria-expanded=${this.open?"true":"false"}
          aria-controls="content"
          aria-disabled=${this.disabled?"true":"false"}
          tabindex=${this.disabled?"-1":"0"}
          @click=${this.handleSummaryClick}
          @keydown=${this.handleSummaryKeyDown}
        >
          <slot name="summary" part="summary" class="details__summary">${this.summary}</slot>

          <span part="summary-icon" class="details__summary-icon">
            <slot name="expand-icon">
              <sl-icon library="system" name=${t?"chevron-left":"chevron-right"}></sl-icon>
            </slot>
            <slot name="collapse-icon">
              <sl-icon library="system" name=${t?"chevron-left":"chevron-right"}></sl-icon>
            </slot>
          </span>
        </header>

        <div class="details__body">
          <slot part="content" id="content" class="details__content" role="region" aria-labelledby="header"></slot>
        </div>
      </div>
    `}};Cs.styles=As,$e([Te(".details")],Cs.prototype,"details",2),$e([Te(".details__header")],Cs.prototype,"header",2),$e([Te(".details__body")],Cs.prototype,"body",2),$e([Te(".details__expand-icon-slot")],Cs.prototype,"expandIconSlot",2),$e([Ce({type:Boolean,reflect:!0})],Cs.prototype,"open",2),$e([Ce()],Cs.prototype,"summary",2),$e([Ce({type:Boolean,reflect:!0})],Cs.prototype,"disabled",2),$e([xe("open",{waitUntilFirstUpdate:!0})],Cs.prototype,"handleOpenChange",1),Cs=$e([ke("sl-details")],Cs),Ke("details.show",{keyframes:[{height:"0",opacity:"0"},{height:"auto",opacity:"1"}],options:{duration:250,easing:"linear"}}),Ke("details.hide",{keyframes:[{height:"auto",opacity:"1"},{height:"0",opacity:"0"}],options:{duration:250,easing:"linear"}});class Es extends it{static styles=r`
        sl-details {
            margin-left: 20px;
            margin-right: 20px;
        }

        .text-field-container {
            overflow: auto;
            max-height: 33vh;
            display: flex;
            flex-direction: column;
        }

        .diff-table {
            width: 100%;
            height: 100%;
            border: none;
        }

        .diff-div {
            height: 33vh;
            display: flex;
            flex-direction: column;
        }

        sl-details::part(base) {
            font-family: Arial, sans-serif;
        }
        sl-details::part(header) {
            font-weight: "bold";
        }
    `;static properties={title:{type:String},files:{type:Object},paths:{type:Object},loadedFiles:{type:Boolean,attribute:!1},diff:{type:String},diffFile:{type:Object}};getNewTabBtnTemplate(t){return R`
            <sl-button style="padding: var(--sl-spacing-x-small)" variant="primary" href=${URL.createObjectURL(t)} target="_blank">
                Open in New Tab
            </sl-button>
        `}getDiffTemplate(){if(this.diffFile){const t=`${this.title}-diff`;return R`
                <sl-tab class="tab" slot="nav" panel=${t}>Diff</sl-tab>
                <sl-tab-panel class="tab-panel" name=${t}>
                    <div class="diff-div" id=${t}>
                        <div>
                            ${this.getNewTabBtnTemplate(this.diffFile)}
                        </div>
                        <!-- Diffs are created in the form of an HTML table so
                        viewed using an iframe  -->
                        <iframe seamless class="diff-table" src="${this.diff}"></iframe>
                    </div>
                </sl-tab-panel>
            `}return R``}getTabTemplate(t,e){const i=`details-panel-${this.title}-${t}`;return R`
            <sl-tab class="tab" slot="nav" panel=${i}>${t}</sl-tab>
            <sl-tab-panel class="tab-panel" name=${i}>
                <div class="text-field-container">
                    <div>
                        ${this.getNewTabBtnTemplate(e)}
                    </div>
                    <pre><code>${No(e.text(),R`Loading...`)}</code></pre>
                </div>
            </sl-tab-panel>
        `}async loadFiles(){for(const t of Object.entries(this.paths))await fetch(t[1]).then((t=>t.blob())).then((e=>{this.files[t[0]]=e}));this.diff&&await fetch(this.diff).then((t=>t.blob())).then((t=>{this.diffFile=t})),this.loadedFiles=!0}connectedCallback(){super.connectedCallback(),!this.files&&this.paths?(this.files={},this.loadedFiles=!1,this.loadFiles()):this.loadedFiles=!0}render(){return this.files?R`
            <sl-details summary=${this.title}>
                <sl-tab-group>
                    ${Object.entries(this.files).map((t=>this.getTabTemplate(t[0],t[1])))}
                    ${this.getDiffTemplate()}
                </sl-tab-group>
            </sl-details>
        `:R``}}customElements.define("sc-file-preview",Es);class Ss{}const Ts=new WeakMap,zs=zo(class extends Fo{render(t){return F}update(t,[e]){var i;const o=e!==this.Y;return o&&void 0!==this.Y&&this.rt(void 0),(o||this.lt!==this.ct)&&(this.Y=e,this.dt=null===(i=t.options)||void 0===i?void 0:i.host,this.rt(this.ct=t.element)),F}rt(t){var e;if("function"==typeof this.Y){const i=null!==(e=this.dt)&&void 0!==e?e:globalThis;let o=Ts.get(i);void 0===o&&(o=new WeakMap,Ts.set(i,o)),void 0!==o.get(this.Y)&&this.Y.call(this.dt,void 0),o.set(this.Y,t),void 0!==t&&this.Y.call(this.dt,t)}else this.Y.value=t}get lt(){var t,e,i;return"function"==typeof this.Y?null===(e=Ts.get(null!==(t=this.dt)&&void 0!==t?t:globalThis))||void 0===e?void 0:e.get(this.Y):null===(i=this.Y)||void 0===i?void 0:i.value}disconnected(){this.lt===this.ct&&this.rt(void 0)}reconnected(){this.rt(this.ct)}});class Ps extends jo{static styles=[jo.styles,r`
        sl-details::part(base) {
            max-width: 30vw;
            font-family: Arial, sans-serif;
            background-color: transparent;
            border: none;
        }
        sl-details::part(header) {
            font-weight: "bold";
            padding: var(--sl-spacing-x-small) var(--sl-spacing-4x-large) var(--sl-spacing-x-small) var(--sl-spacing-x-small);
            font-size: 12px;
        }
        `];tableRef=(()=>new Ss)();removeDetailsEl(t){for(const e of t.childNodes)if("TR"===e.tagName)for(const t of e.childNodes)for(const e of t.childNodes)"SL-DETAILS"===e.tagName&&t.removeChild(e);return t}copyTable(){const t=window.getSelection();t.removeAllRanges();const e=document.createRange();e.selectNodeContents(this.tableRef.value),t.addRange(e),this.removeDetailsEl(t.anchorNode),document.execCommand("copy"),t.removeAllRanges(),this.requestUpdate()}parseMetric(t){const e=t[0].split("|");return R`
            <td rowspan=${t[1]}>
                <strong>${e[0]}</strong>
                <sl-details summary="Description">
                    ${e[1]}
                </sl-details>
            </td>
        `}parseSummaryFunc(t){const[e,i]=t.split("|");return R`
            <td class="td-value">
                ${i?R`<abbr title=${i}>${e}</abbr>`:R`${e}`}
            </td>
        `}async parseSrc(){let t,e=R``;for await(const i of this.makeTextFileLineIterator(this.file)){const o=i.split(";"),s=o[0];if(o.shift(),"H"===s)for(const t of o)e=R`${e}<th>${t}</th>`,this.cols=this.cols+1;else if("M"===s)t=this.parseMetric(o);else{const i=R`${o.map((t=>this.parseSummaryFunc(t)))}`;e=R`
                    ${e}
                    <tr>
                      ${t}
                      ${i}
                    </tr>
                `,t&&(t=void 0)}}return e=R`<table ${zs(this.tableRef)} width=${this.getWidth(this.cols)}>${e}</table>`,R`
            <div style="display:flex;">
                ${e}
                <sl-button style="margin-left:5px" @click=${this.copyTable}>Copy table</sl-button>
            </div>
        `}constructor(){super(),this.cols=0}connectedCallback(){super.connectedCallback(),this.parseSrc().then((t=>{this.template=t}))}}customElements.define("sc-smry-tbl",Ps);class Ls extends it{static styles=r`
        sl-alert {
            margin-left: 20px;
            margin-right: 20px;
        }
  `;static properties={paths:{type:Array},alerts:{type:Array},fpreviews:{type:Array},smrytblpath:{type:String},smrytblfile:{type:Blob}};summaryTableTemplate(){return R`
            <div style="margin-left: 2em; margin-right: 1em;">
                <sc-smry-tbl .file="${this.smrytblfile}"></sc-smry-tbl>
            </div>
        `}render(){return this.smrytblpath&&!this.smrytblfile&&fetch(this.smrytblpath).then((t=>t.blob())).then((t=>{this.smrytblfile=t})),R`
            <br>
            ${this.smrytblfile?this.summaryTableTemplate():R``}

            ${this.alerts.length>0?R`
                    <br>
                    <sl-alert variant="primary" open>
                        <ul>
                            ${this.alerts.map((t=>R`<li>${t}</li>`))}
                        </ul>
                    </sl-alert>
                    <br>
                `:R``}

            ${this.fpreviews?this.fpreviews.map((t=>R`
                    <sc-file-preview .title=${t.title}
                        .diff=${t.diff} .diffFile=${t.diffFile}
                        .paths=${t.paths} .files=${t.files}>
                    </sc-file-preview>
                    <br>
                `)):R``}
            <div style="display: flex; flex-direction: column;">
                ${this.paths?this.paths.map((t=>R`<sc-diagram path=${t}></sc-diagram>`)):R``}
            </div>
        `}}customElements.define("sc-data-tab",Ls),customElements.define("sc-tab-panel",class extends it{static properties={tab:{type:Object}};selectTabInTabTree(t){const e=this.renderRoot.querySelectorAll("sl-tree-item[selected]");for(const t of e)t.selected=!1;const i=this.renderRoot.querySelectorAll("sl-tree-item[expanded]");for(const t of i)t.expanded=!1;let o=this.renderRoot.getElementById(`${t}-tree`);for(o.selected=!0;"SL-TREE-ITEM"===o.tagName;)o.expanded=!0,o=o.parentElement}hasDataTab(t){return this.dataTabs.includes(t)}show(t){if(!this.hasDataTab(t))return;if(this.activeDataTab?.id===t)return;this.activeDataTab&&(this.activeDataTab.hidden=!0);const e=this.renderRoot.getElementById(t);this.activeDataTab=e,e&&(e.hidden=!1),this.selectTabInTabTree(t)}tabPanesTemplate(t){let e=R``;for(const i of t.tabs)e=i.tabs?R`${e}${this.tabPanesTemplate(i)}`:R`${e}
                    <sc-data-tab hidden id=${i.id} tabname=${i.name}
                        .smrytblpath=${i.smrytblpath} .smrytblfile=${i.smrytblfile}
                        .paths=${i.ppaths} .fpreviews=${i.fpreviews}
                        .dir=${i.dir} .alerts=${i.alerts}>
                    </sc-data-tab>`;return e}firstUpdated(){this.show(this.firstTab)}treeItemTemplate(t){return t.tabs?R`
            ${t.name}
            ${t.tabs.map((t=>R`
                    <sl-tree-item id=${`${t.id}-tree`} @click=${t.tabs?()=>{}:()=>{location.hash=t.id}}>
                        ${this.treeItemTemplate(t)}
                    </sl-tree-item>
                `))}
        `:(this.dataTabs.push(t.id),this.firstTab||(this.firstTab=t.id),t.name)}render(){return this.tab?R`
            <sl-split-panel position=20 snap="0% 25%" style="--divider-width: 2px;">
                <div style="height: calc(100vh - 2em); overflow-y: scroll; overflox-x: hidden;" selection="leaf" slot="start">
                    <sl-tree selection="leaf" slot="start">
                        ${this.treeItemTemplate(this.tab)}
                    </sl-tree>
                </div>
                <div style="height: calc(100vh - 2em); overflow-y:scroll;" slot="end">
                    ${this.tabPanesTemplate(this.tab)}
                </div>
            </sl-split-panel>
        `:R``}constructor(){super(),this.dataTabs=[],this.firstTab=""}});class Is extends it{static styles=r`
        /*
         * By default, inactive Shoelace tabs have 'display: none' which breaks Plotly legends.
         * Therefore we make inactive tabs invisible in our own way using the following two css
         * classes:
         */
        sl-tab-panel{
            display: block !important;
            height: 0px !important;
            overflow: hidden;
        }

        sl-tab-panel[active] {
            display: block !important;
            height: auto !important;
        }

        /*
         * The hierarchy of tabs can go up to and beyond 5 levels of depth. Remove the padding on
         * tab panels so that there is no space between each level of tabs.
         */
        .tab-panel::part(base) {
            padding: 0px 0px;
        }
        /*
         * Also reduce the top and bottom padding of tabs as it makes them easier to read.
         */
        .tab::part(base) {
            padding-bottom: var(--sl-spacing-x-small);
            padding-top: var(--sl-spacing-x-small);
            font-family: Arial, sans-serif;
        }

        /*
         * Specify height of tabs to match the button to toggle the report header.
         */
        sl-tab-group::part(tabs) {
            height: 2rem;
        }
    `;static properties={tabs:{type:Object}};get _tabPanels(){return this.renderRoot.querySelectorAll("sc-tab-panel")}get _tabGroup(){return this.renderRoot.querySelector("sl-tab-group")}getTabPanel(t){for(const e of this._tabPanels)if(e.hasDataTab(t))return e}getActiveTab(){const t=this._tabGroup.querySelectorAll("sl-tab");for(const e of t)if(e.active)return e;throw Error("BUG: unable to find active tab")}getActiveDataTab(){const t=this.getActiveTab();for(const e of this._tabPanels)if(e.tab.name===t.panel)return e.activeDataTab;throw Error("BUG: unable to find active data tab")}show(t=location.hash.substring(1)){for(const e of this._tabPanels)e.show(t)}firstUpdated(){this.tabChangeHandler=()=>{location.href=`#${this.getActiveDataTab().id}`},this._tabGroup.addEventListener("sl-tab-show",this.tabChangeHandler),this._tabGroup.updateComplete.then((()=>{const t=location.hash.substring(1);if(!t)return void(location.hash=`${this._tabPanels[0].firstTab}`);const e=this.getTabPanel(t);e.updateComplete.then((()=>{e.show(t),this._tabGroup.show(e.parentElement.name)}))}))}connectedCallback(){super.connectedCallback(),this.hashHandler=()=>{this.show()},window.addEventListener("hashchange",this.hashHandler,!1)}disconnectedCallback(){window.removeEventListener("hashchange",this.hashHandler),this._tabGroup.removeEventListener("sl-tab-show",this.tabChangeHandler)}render(){return this.tabs?R`
            <sl-tab-group>
                ${this.tabs.map((t=>R`
                    <sl-tab class="tab" slot="nav" panel="${t.name}">${t.name}</sl-tab>
                    <sl-tab-panel class="tab-panel" name="${t.name}">
                        <sc-tab-panel .tab=${t}></sc-tab-panel>
                    </sl-tab-panel>
                `))}
            </sl-tab-group>
      `:R``}}customElements.define("sc-tab-group",Is);class Os extends it{static properties={introtbl:{type:Object},src:{type:String},reportInfo:{type:Object},toolname:{type:String},titleDescr:{type:String},tabs:{type:Object},fetchFailed:{type:Boolean,attribute:!1}};static styles=r`
        * {
            font-family: Arial, sans-serif;
        }

        .report-head {
            display: flex;
            flex-direction: column;
            align-items: center;
            transition: 0.5s;
            max-height: 100vh;
            overflow: hidden;
        }

        .cors-warning {
            display: flex;
            flex-direction: column;
        }

        .sticky {
            position: sticky;
            top: 0;
            height: 100vh;
        }

        .toggle-header-btn {
            position: absolute;
            top: 0;
            right: 0;
            z-index: 1;
        }

        // Hide the close button as the dialog is not closable.
        sl-dialog::part(close-button) {
            visibility: hidden;
        }
    `;get _corsWarning(){return this.renderRoot.querySelector(".cors-warning")}initRepProps(){this.reportTitle=this.reportInfo.title,this.reportDescr=this.reportInfo.descr,this.toolname=this.reportInfo.toolname,this.toolver=this.reportInfo.toolver,this.logpath=this.reportInfo.logpath}generateTabIDs(t){for(const e of t){e.tabs&&(e.tabs=this.generateTabIDs(e.tabs));const t=e.name.replace(/\s/g,"-").replace("%","Percent").replace(/[^a-zA-Z0-9-]+/g,"");this.tabIDs.has(t)?(this.tabIDs.set(t,this.tabIDs.get(t)+1),e.id=`${t}-${this.tabIDs.get(t)}`):(this.tabIDs.set(t,0),e.id=t)}return t}parseReportInfo(t){this.reportInfo=t,this.initRepProps(),t.intro_tbl&&fetch(t.intro_tbl).then((t=>t.blob())).then((t=>{this.introtbl=t})),fetch(t.tab_file).then((t=>t.json())).then((async t=>{this.tabs=this.generateTabIDs(t)}))}connectedCallback(){fetch(this.src).then((t=>t.json())).then((t=>this.parseReportInfo(t))).catch((t=>{if(!(t instanceof TypeError))throw t;this.fetchFailed=!0})),super.connectedCallback()}firstUpdated(){const t=this.renderRoot.querySelector(".report-info-dialog");this.renderRoot.querySelector(".open-info-dialog").addEventListener("click",(()=>t.show()))}updated(t){t.has("fetchFailed")&&this.fetchFailed&&this._corsWarning.addEventListener("sl-request-close",(t=>{t.preventDefault()}))}corsWarning(){return R`
            <sl-dialog class="cors-warning" label="Failed to load report" open>
                <p>
                    Due to browser security limitations your report could not be retrieved. Please
                    upload your report directory using the upload button below:
                </p>
                <input @change="${this.processUploadedFiles}" id="upload-files" directory webkitdirectory type="file">
                <sl-divider></sl-divider>
                <p>
                    If you have tried uploading your report directory with the button above and it 
                    is still not rendering properly, please see the following documentation for
                    details on other methods of viewing reports:
                    <a href="https://intel.github.io/wult/pages/howto-view-local.html#open-wult-reports-locally"> here</a>.
                </p>
            </sl-dialog>
        `}findFile(t){const e=Object.keys(this.files);for(const i of e)if(i.endsWith(t))return this.files[i];throw Error(`unable to find an uploaded file ending with '${t}'.`)}async resolveTabFile(t,e){return t?await fetch(e).then((t=>t.blob())):this.findFile(e)}async extractTabs(t,e){for(const i of t){if(i.smrytblpath&&(i.smrytblfile=await this.resolveTabFile(e,i.smrytblpath)),i.fpreviews)for(const t of i.fpreviews){t.files={};for(const[i,o]of Object.entries(t.paths))t.files[i]=await this.resolveTabFile(e,o);t.diff&&(t.diffFile=await this.resolveTabFile(e,t.diff))}i.tabs&&(i.tabs=await this.extractTabs(i.tabs,e))}return this.generateTabIDs(t)}async processUploadedFiles(){const t=this.renderRoot.getElementById("upload-files");this.files={};for(const e of t.files)this.files[e.webkitRelativePath]=e;const e=await this.findFile("report_info.json").arrayBuffer();this.reportInfo=JSON.parse((new TextDecoder).decode(e)),this.introtbl=this.findFile(this.reportInfo.intro_tbl);const i=await this.findFile(this.reportInfo.tab_file).arrayBuffer().then((t=>JSON.parse((new TextDecoder).decode(t))));this.tabs=await this.extractTabs(i,!1),this.initRepProps(),this.fetchFailed=!1}constructor(){super(),this.fetchFailed=!1,this.reportInfo={},this.tabIDs=new Map,this.headerExpanded=!0}toggleHeader(){const t=this.renderRoot.querySelector(".report-head");this.headerExpanded?t.style.maxHeight="0vh":t.style.maxHeight="100vh",this.headerExpanded=!this.headerExpanded}reportInfoTemplate(){return R`
        <sl-dialog class="report-info-dialog" label="Report Info">
            ${this.toolname&&this.toolver?R`Generated with <i>'${this.toolname} v${this.toolver}'</i>`:R``}
            <br>
            <br>
            ${this.logpath?R`<u><i><a target="_blank" href=${this.logpath}>Report Generation Log</a></i></u>`:R``}
        </sl-dialog>
        `}render(){return this.fetchFailed?this.corsWarning():R`
            ${this.reportInfoTemplate()}
            <div class="report-head">
                <div style="position: relative;left: 45vw;top: 1em;height: 0px;">
                    <sl-tooltip content="Report info">
                        <sl-button class="open-info-dialog">
                            <i>i</i>
                        </sl-button>
                    </sl-tooltip>
                </div>
                <div style="display:flex; flex-direction: column; align-items: center">
                    ${this.reportTitle?R`<h1>${this.reportTitle}</h1>`:R``}
                    ${this.reportDescr?R`<p>${this.reportDescr}</p>`:R``}
                    ${this.introtbl?R`<sc-intro-tbl .file=${this.introtbl}></sc-intro-tbl>`:R``}
                </div>
            </div>
            <div class="sticky">
                <sl-button size="small" class="toggle-header-btn" @click=${this.toggleHeader}>
                    Toggle Header
                </sl-button>
                ${this.tabs?R`<sc-tab-group .tabs=${this.tabs}></sc-tab-group>`:R``}
            </div>
        `}}customElements.define("sc-report-page",Os),yi("shoelace")})();