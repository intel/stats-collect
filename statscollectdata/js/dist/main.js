/*! For license information please see main.js.LICENSE.txt */
(()=>{"use strict";const t=window,e=t.ShadowRoot&&(void 0===t.ShadyCSS||t.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,i=Symbol(),o=new WeakMap;class s{constructor(t,e,o){if(this._$cssResult$=!0,o!==i)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const i=this.t;if(e&&void 0===t){const e=void 0!==i&&1===i.length;e&&(t=o.get(i)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),e&&o.set(i,t))}return t}toString(){return this.cssText}}const r=(t,...e)=>{const o=1===t.length?t[0]:e.reduce((e,i,o)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[o+1],t[0]);return new s(o,t,i)},n=e?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new s("string"==typeof t?t:t+"",void 0,i))(e)})(t):t;var a;const l=window,c=l.trustedTypes,d=c?c.emptyScript:"",h=l.reactiveElementPolyfillSupport,u={toAttribute(t,e){switch(e){case Boolean:t=t?d:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},p=(t,e)=>e!==t&&(e==e||t==t),b={attribute:!0,type:String,converter:u,reflect:!1,hasChanged:p},f="finalized";class m extends HTMLElement{constructor(){super(),this._$Ei=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$El=null,this._$Eu()}static addInitializer(t){var e;this.finalize(),(null!==(e=this.h)&&void 0!==e?e:this.h=[]).push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach((e,i)=>{const o=this._$Ep(i,e);void 0!==o&&(this._$Ev.set(o,i),t.push(o))}),t}static createProperty(t,e=b){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const i="symbol"==typeof t?Symbol():"__"+t,o=this.getPropertyDescriptor(t,i,e);void 0!==o&&Object.defineProperty(this.prototype,t,o)}}static getPropertyDescriptor(t,e,i){return{get(){return this[e]},set(o){const s=this[t];this[e]=o,this.requestUpdate(t,s,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||b}static finalize(){if(this.hasOwnProperty(f))return!1;this[f]=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),void 0!==t.h&&(this.h=[...t.h]),this.elementProperties=new Map(t.elementProperties),this._$Ev=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const i of e)this.createProperty(i,t[i])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(n(t))}else void 0!==t&&e.push(n(t));return e}static _$Ep(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}_$Eu(){var t;this._$E_=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$Eg(),this.requestUpdate(),null===(t=this.constructor.h)||void 0===t||t.forEach(t=>t(this))}addController(t){var e,i;(null!==(e=this._$ES)&&void 0!==e?e:this._$ES=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(i=t.hostConnected)||void 0===i||i.call(t))}removeController(t){var e;null===(e=this._$ES)||void 0===e||e.splice(this._$ES.indexOf(t)>>>0,1)}_$Eg(){this.constructor.elementProperties.forEach((t,e)=>{this.hasOwnProperty(e)&&(this._$Ei.set(e,this[e]),delete this[e])})}createRenderRoot(){var i;const o=null!==(i=this.shadowRoot)&&void 0!==i?i:this.attachShadow(this.constructor.shadowRootOptions);return((i,o)=>{e?i.adoptedStyleSheets=o.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet):o.forEach(e=>{const o=document.createElement("style"),s=t.litNonce;void 0!==s&&o.setAttribute("nonce",s),o.textContent=e.cssText,i.appendChild(o)})})(o,this.constructor.elementStyles),o}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)})}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)})}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$EO(t,e,i=b){var o;const s=this.constructor._$Ep(t,i);if(void 0!==s&&!0===i.reflect){const r=(void 0!==(null===(o=i.converter)||void 0===o?void 0:o.toAttribute)?i.converter:u).toAttribute(e,i.type);this._$El=t,null==r?this.removeAttribute(s):this.setAttribute(s,r),this._$El=null}}_$AK(t,e){var i;const o=this.constructor,s=o._$Ev.get(t);if(void 0!==s&&this._$El!==s){const t=o.getPropertyOptions(s),r="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==(null===(i=t.converter)||void 0===i?void 0:i.fromAttribute)?t.converter:u;this._$El=s,this[s]=r.fromAttribute(e,t.type),this._$El=null}}requestUpdate(t,e,i){let o=!0;void 0!==t&&(((i=i||this.constructor.getPropertyOptions(t)).hasChanged||p)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===i.reflect&&this._$El!==t&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(t,i))):o=!1),!this.isUpdatePending&&o&&(this._$E_=this._$Ej())}async _$Ej(){this.isUpdatePending=!0;try{await this._$E_}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Ei&&(this._$Ei.forEach((t,e)=>this[e]=t),this._$Ei=void 0);let e=!1;const i=this._$AL;try{e=this.shouldUpdate(i),e?(this.willUpdate(i),null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)}),this.update(i)):this._$Ek()}catch(t){throw e=!1,this._$Ek(),t}e&&this._$AE(i)}willUpdate(t){}_$AE(t){var e;null===(e=this._$ES)||void 0===e||e.forEach(t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)}),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$Ek(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$E_}shouldUpdate(t){return!0}update(t){void 0!==this._$EC&&(this._$EC.forEach((t,e)=>this._$EO(e,this[e],t)),this._$EC=void 0),this._$Ek()}updated(t){}firstUpdated(t){}}var g;m[f]=!0,m.elementProperties=new Map,m.elementStyles=[],m.shadowRootOptions={mode:"open"},null==h||h({ReactiveElement:m}),(null!==(a=l.reactiveElementVersions)&&void 0!==a?a:l.reactiveElementVersions=[]).push("1.6.3");const v=window,y=v.trustedTypes,w=y?y.createPolicy("lit-html",{createHTML:t=>t}):void 0,_="$lit$",x=`lit$${(Math.random()+"").slice(9)}$`,$="?"+x,k=`<${$}>`,A=document,C=()=>A.createComment(""),E=t=>null===t||"object"!=typeof t&&"function"!=typeof t,S=Array.isArray,T=t=>S(t)||"function"==typeof(null==t?void 0:t[Symbol.iterator]),z="[ \t\n\f\r]",P=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,I=/-->/g,L=/>/g,O=RegExp(`>|${z}(?:([^\\s"'>=/]+)(${z}*=${z}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),F=/'/g,R=/"/g,D=/^(?:script|style|textarea|title)$/i,B=t=>(e,...i)=>({_$litType$:t,strings:e,values:i}),N=B(1),H=(B(2),Symbol.for("lit-noChange")),U=Symbol.for("lit-nothing"),M=new WeakMap,V=A.createTreeWalker(A,129,null,!1);function j(t,e){if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==w?w.createHTML(e):e}const W=(t,e)=>{const i=t.length-1,o=[];let s,r=2===e?"<svg>":"",n=P;for(let e=0;e<i;e++){const i=t[e];let a,l,c=-1,d=0;for(;d<i.length&&(n.lastIndex=d,l=n.exec(i),null!==l);)d=n.lastIndex,n===P?"!--"===l[1]?n=I:void 0!==l[1]?n=L:void 0!==l[2]?(D.test(l[2])&&(s=RegExp("</"+l[2],"g")),n=O):void 0!==l[3]&&(n=O):n===O?">"===l[0]?(n=null!=s?s:P,c=-1):void 0===l[1]?c=-2:(c=n.lastIndex-l[2].length,a=l[1],n=void 0===l[3]?O:'"'===l[3]?R:F):n===R||n===F?n=O:n===I||n===L?n=P:(n=O,s=void 0);const h=n===O&&t[e+1].startsWith("/>")?" ":"";r+=n===P?i+k:c>=0?(o.push(a),i.slice(0,c)+_+i.slice(c)+x+h):i+x+(-2===c?(o.push(void 0),e):h)}return[j(t,r+(t[i]||"<?>")+(2===e?"</svg>":"")),o]};class q{constructor({strings:t,_$litType$:e},i){let o;this.parts=[];let s=0,r=0;const n=t.length-1,a=this.parts,[l,c]=W(t,e);if(this.el=q.createElement(l,i),V.currentNode=this.el.content,2===e){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(o=V.nextNode())&&a.length<n;){if(1===o.nodeType){if(o.hasAttributes()){const t=[];for(const e of o.getAttributeNames())if(e.endsWith(_)||e.startsWith(x)){const i=c[r++];if(t.push(e),void 0!==i){const t=o.getAttribute(i.toLowerCase()+_).split(x),e=/([.?@])?(.*)/.exec(i);a.push({type:1,index:s,name:e[2],strings:t,ctor:"."===e[1]?X:"?"===e[1]?Q:"@"===e[1]?tt:Y})}else a.push({type:6,index:s})}for(const e of t)o.removeAttribute(e)}if(D.test(o.tagName)){const t=o.textContent.split(x),e=t.length-1;if(e>0){o.textContent=y?y.emptyScript:"";for(let i=0;i<e;i++)o.append(t[i],C()),V.nextNode(),a.push({type:2,index:++s});o.append(t[e],C())}}}else if(8===o.nodeType)if(o.data===$)a.push({type:2,index:s});else{let t=-1;for(;-1!==(t=o.data.indexOf(x,t+1));)a.push({type:7,index:s}),t+=x.length-1}s++}}static createElement(t,e){const i=A.createElement("template");return i.innerHTML=t,i}}function K(t,e,i=t,o){var s,r,n,a;if(e===H)return e;let l=void 0!==o?null===(s=i._$Co)||void 0===s?void 0:s[o]:i._$Cl;const c=E(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==c&&(null===(r=null==l?void 0:l._$AO)||void 0===r||r.call(l,!1),void 0===c?l=void 0:(l=new c(t),l._$AT(t,i,o)),void 0!==o?(null!==(n=(a=i)._$Co)&&void 0!==n?n:a._$Co=[])[o]=l:i._$Cl=l),void 0!==l&&(e=K(t,l._$AS(t,e.values),l,o)),e}class G{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){var e;const{el:{content:i},parts:o}=this._$AD,s=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:A).importNode(i,!0);V.currentNode=s;let r=V.nextNode(),n=0,a=0,l=o[0];for(;void 0!==l;){if(n===l.index){let e;2===l.type?e=new Z(r,r.nextSibling,this,t):1===l.type?e=new l.ctor(r,l.name,l.strings,this,t):6===l.type&&(e=new et(r,this,t)),this._$AV.push(e),l=o[++a]}n!==(null==l?void 0:l.index)&&(r=V.nextNode(),n++)}return V.currentNode=A,s}v(t){let e=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}}class Z{constructor(t,e,i,o){var s;this.type=2,this._$AH=U,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=o,this._$Cp=null===(s=null==o?void 0:o.isConnected)||void 0===s||s}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cp}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===(null==t?void 0:t.nodeType)&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=K(this,t,e),E(t)?t===U||null==t||""===t?(this._$AH!==U&&this._$AR(),this._$AH=U):t!==this._$AH&&t!==H&&this._(t):void 0!==t._$litType$?this.g(t):void 0!==t.nodeType?this.$(t):T(t)?this.T(t):this._(t)}k(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}$(t){this._$AH!==t&&(this._$AR(),this._$AH=this.k(t))}_(t){this._$AH!==U&&E(this._$AH)?this._$AA.nextSibling.data=t:this.$(A.createTextNode(t)),this._$AH=t}g(t){var e;const{values:i,_$litType$:o}=t,s="number"==typeof o?this._$AC(t):(void 0===o.el&&(o.el=q.createElement(j(o.h,o.h[0]),this.options)),o);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===s)this._$AH.v(i);else{const t=new G(s,this),e=t.u(this.options);t.v(i),this.$(e),this._$AH=t}}_$AC(t){let e=M.get(t.strings);return void 0===e&&M.set(t.strings,e=new q(t)),e}T(t){S(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let i,o=0;for(const s of t)o===e.length?e.push(i=new Z(this.k(C()),this.k(C()),this,this.options)):i=e[o],i._$AI(s),o++;o<e.length&&(this._$AR(i&&i._$AB.nextSibling,o),e.length=o)}_$AR(t=this._$AA.nextSibling,e){var i;for(null===(i=this._$AP)||void 0===i||i.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cp=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}}class Y{constructor(t,e,i,o,s){this.type=1,this._$AH=U,this._$AN=void 0,this.element=t,this.name=e,this._$AM=o,this.options=s,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=U}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,i,o){const s=this.strings;let r=!1;if(void 0===s)t=K(this,t,e,0),r=!E(t)||t!==this._$AH&&t!==H,r&&(this._$AH=t);else{const o=t;let n,a;for(t=s[0],n=0;n<s.length-1;n++)a=K(this,o[i+n],e,n),a===H&&(a=this._$AH[n]),r||(r=!E(a)||a!==this._$AH[n]),a===U?t=U:t!==U&&(t+=(null!=a?a:"")+s[n+1]),this._$AH[n]=a}r&&!o&&this.j(t)}j(t){t===U?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}}class X extends Y{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===U?void 0:t}}const J=y?y.emptyScript:"";class Q extends Y{constructor(){super(...arguments),this.type=4}j(t){t&&t!==U?this.element.setAttribute(this.name,J):this.element.removeAttribute(this.name)}}class tt extends Y{constructor(t,e,i,o,s){super(t,e,i,o,s),this.type=5}_$AI(t,e=this){var i;if((t=null!==(i=K(this,t,e,0))&&void 0!==i?i:U)===H)return;const o=this._$AH,s=t===U&&o!==U||t.capture!==o.capture||t.once!==o.once||t.passive!==o.passive,r=t!==U&&(o===U||s);s&&this.element.removeEventListener(this.name,this,o),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,i;"function"==typeof this._$AH?this._$AH.call(null!==(i=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==i?i:this.element,t):this._$AH.handleEvent(t)}}class et{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){K(this,t)}}const it={O:_,P:x,A:$,C:1,M:W,L:G,R:T,D:K,I:Z,V:Y,H:Q,N:tt,U:X,F:et},ot=v.litHtmlPolyfillSupport;var st,rt;null==ot||ot(q,Z),(null!==(g=v.litHtmlVersions)&&void 0!==g?g:v.litHtmlVersions=[]).push("2.8.0");class nt extends m{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var t,e;const i=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=i.firstChild),i}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,i)=>{var o,s;const r=null!==(o=null==i?void 0:i.renderBefore)&&void 0!==o?o:e;let n=r._$litPart$;if(void 0===n){const t=null!==(s=null==i?void 0:i.renderBefore)&&void 0!==s?s:null;r._$litPart$=n=new Z(e.insertBefore(C(),t),t,void 0,null!=i?i:{})}return n._$AI(t),n})(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!1)}render(){return H}}nt.finalized=!0,nt._$litElement$=!0,null===(st=globalThis.litElementHydrateSupport)||void 0===st||st.call(globalThis,{LitElement:nt});const at=globalThis.litElementPolyfillSupport;null==at||at({LitElement:nt}),(null!==(rt=globalThis.litElementVersions)&&void 0!==rt?rt:globalThis.litElementVersions=[]).push("3.3.3");const lt=globalThis,ct=lt.ShadowRoot&&(void 0===lt.ShadyCSS||lt.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,dt=Symbol(),ht=new WeakMap;class ut{constructor(t,e,i){if(this._$cssResult$=!0,i!==dt)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(ct&&void 0===t){const i=void 0!==e&&1===e.length;i&&(t=ht.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),i&&ht.set(e,t))}return t}toString(){return this.cssText}}const pt=(t,...e)=>{const i=1===t.length?t[0]:e.reduce((e,i,o)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[o+1],t[0]);return new ut(i,t,dt)},bt=ct?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new ut("string"==typeof t?t:t+"",void 0,dt))(e)})(t):t,{is:ft,defineProperty:mt,getOwnPropertyDescriptor:gt,getOwnPropertyNames:vt,getOwnPropertySymbols:yt,getPrototypeOf:wt}=Object,_t=globalThis,xt=_t.trustedTypes,$t=xt?xt.emptyScript:"",kt=_t.reactiveElementPolyfillSupport,At=(t,e)=>t,Ct={toAttribute(t,e){switch(e){case Boolean:t=t?$t:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},Et=(t,e)=>!ft(t,e),St={attribute:!0,type:String,converter:Ct,reflect:!1,useDefault:!1,hasChanged:Et};Symbol.metadata??=Symbol("metadata"),_t.litPropertyMetadata??=new WeakMap;class Tt extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=St){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){const i=Symbol(),o=this.getPropertyDescriptor(t,i,e);void 0!==o&&mt(this.prototype,t,o)}}static getPropertyDescriptor(t,e,i){const{get:o,set:s}=gt(this.prototype,t)??{get(){return this[e]},set(t){this[e]=t}};return{get:o,set(e){const r=o?.call(this);s?.call(this,e),this.requestUpdate(t,r,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??St}static _$Ei(){if(this.hasOwnProperty(At("elementProperties")))return;const t=wt(this);t.finalize(),void 0!==t.l&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(At("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(At("properties"))){const t=this.properties,e=[...vt(t),...yt(t)];for(const i of e)this.createProperty(i,t[i])}const t=this[Symbol.metadata];if(null!==t){const e=litPropertyMetadata.get(t);if(void 0!==e)for(const[t,i]of e)this.elementProperties.set(t,i)}this._$Eh=new Map;for(const[t,e]of this.elementProperties){const i=this._$Eu(t,e);void 0!==i&&this._$Eh.set(i,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(bt(t))}else void 0!==t&&e.push(bt(t));return e}static _$Eu(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),void 0!==this.renderRoot&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){const t=new Map,e=this.constructor.elementProperties;for(const i of e.keys())this.hasOwnProperty(i)&&(t.set(i,this[i]),delete this[i]);t.size>0&&(this._$Ep=t)}createRenderRoot(){const t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((t,e)=>{if(ct)t.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const i of e){const e=document.createElement("style"),o=lt.litNonce;void 0!==o&&e.setAttribute("nonce",o),e.textContent=i.cssText,t.appendChild(e)}})(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$ET(t,e){const i=this.constructor.elementProperties.get(t),o=this.constructor._$Eu(t,i);if(void 0!==o&&!0===i.reflect){const s=(void 0!==i.converter?.toAttribute?i.converter:Ct).toAttribute(e,i.type);this._$Em=t,null==s?this.removeAttribute(o):this.setAttribute(o,s),this._$Em=null}}_$AK(t,e){const i=this.constructor,o=i._$Eh.get(t);if(void 0!==o&&this._$Em!==o){const t=i.getPropertyOptions(o),s="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==t.converter?.fromAttribute?t.converter:Ct;this._$Em=o;const r=s.fromAttribute(e,t.type);this[o]=r??this._$Ej?.get(o)??r,this._$Em=null}}requestUpdate(t,e,i){if(void 0!==t){const o=this.constructor,s=this[t];if(i??=o.getPropertyOptions(t),!((i.hasChanged??Et)(s,e)||i.useDefault&&i.reflect&&s===this._$Ej?.get(t)&&!this.hasAttribute(o._$Eu(t,i))))return;this.C(t,e,i)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(t,e,{useDefault:i,reflect:o,wrapped:s},r){i&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,r??e??this[t]),!0!==s||void 0!==r)||(this._$AL.has(t)||(this.hasUpdated||i||(e=void 0),this._$AL.set(t,e)),!0===o&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[t,e]of this._$Ep)this[t]=e;this._$Ep=void 0}const t=this.constructor.elementProperties;if(t.size>0)for(const[e,i]of t){const{wrapped:t}=i,o=this[e];!0!==t||this._$AL.has(e)||void 0===o||this.C(e,void 0,i,o)}}let t=!1;const e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(t=>t.hostUpdate?.()),this.update(e)):this._$EM()}catch(e){throw t=!1,this._$EM(),e}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(t){}firstUpdated(t){}}Tt.elementStyles=[],Tt.shadowRootOptions={mode:"open"},Tt[At("elementProperties")]=new Map,Tt[At("finalized")]=new Map,kt?.({ReactiveElement:Tt}),(_t.reactiveElementVersions??=[]).push("2.1.1");const zt=globalThis,Pt=zt.trustedTypes,It=Pt?Pt.createPolicy("lit-html",{createHTML:t=>t}):void 0,Lt="$lit$",Ot=`lit$${Math.random().toFixed(9).slice(2)}$`,Ft="?"+Ot,Rt=`<${Ft}>`,Dt=document,Bt=()=>Dt.createComment(""),Nt=t=>null===t||"object"!=typeof t&&"function"!=typeof t,Ht=Array.isArray,Ut=t=>Ht(t)||"function"==typeof t?.[Symbol.iterator],Mt="[ \t\n\f\r]",Vt=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,jt=/-->/g,Wt=/>/g,qt=RegExp(`>|${Mt}(?:([^\\s"'>=/]+)(${Mt}*=${Mt}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),Kt=/'/g,Gt=/"/g,Zt=/^(?:script|style|textarea|title)$/i,Yt=t=>(e,...i)=>({_$litType$:t,strings:e,values:i}),Xt=Yt(1),Jt=Yt(2),Qt=Yt(3),te=Symbol.for("lit-noChange"),ee=Symbol.for("lit-nothing"),ie=new WeakMap,oe=Dt.createTreeWalker(Dt,129);function se(t,e){if(!Ht(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==It?It.createHTML(e):e}const re=(t,e)=>{const i=t.length-1,o=[];let s,r=2===e?"<svg>":3===e?"<math>":"",n=Vt;for(let e=0;e<i;e++){const i=t[e];let a,l,c=-1,d=0;for(;d<i.length&&(n.lastIndex=d,l=n.exec(i),null!==l);)d=n.lastIndex,n===Vt?"!--"===l[1]?n=jt:void 0!==l[1]?n=Wt:void 0!==l[2]?(Zt.test(l[2])&&(s=RegExp("</"+l[2],"g")),n=qt):void 0!==l[3]&&(n=qt):n===qt?">"===l[0]?(n=s??Vt,c=-1):void 0===l[1]?c=-2:(c=n.lastIndex-l[2].length,a=l[1],n=void 0===l[3]?qt:'"'===l[3]?Gt:Kt):n===Gt||n===Kt?n=qt:n===jt||n===Wt?n=Vt:(n=qt,s=void 0);const h=n===qt&&t[e+1].startsWith("/>")?" ":"";r+=n===Vt?i+Rt:c>=0?(o.push(a),i.slice(0,c)+Lt+i.slice(c)+Ot+h):i+Ot+(-2===c?e:h)}return[se(t,r+(t[i]||"<?>")+(2===e?"</svg>":3===e?"</math>":"")),o]};class ne{constructor({strings:t,_$litType$:e},i){let o;this.parts=[];let s=0,r=0;const n=t.length-1,a=this.parts,[l,c]=re(t,e);if(this.el=ne.createElement(l,i),oe.currentNode=this.el.content,2===e||3===e){const t=this.el.content.firstChild;t.replaceWith(...t.childNodes)}for(;null!==(o=oe.nextNode())&&a.length<n;){if(1===o.nodeType){if(o.hasAttributes())for(const t of o.getAttributeNames())if(t.endsWith(Lt)){const e=c[r++],i=o.getAttribute(t).split(Ot),n=/([.?@])?(.*)/.exec(e);a.push({type:1,index:s,name:n[2],strings:i,ctor:"."===n[1]?he:"?"===n[1]?ue:"@"===n[1]?pe:de}),o.removeAttribute(t)}else t.startsWith(Ot)&&(a.push({type:6,index:s}),o.removeAttribute(t));if(Zt.test(o.tagName)){const t=o.textContent.split(Ot),e=t.length-1;if(e>0){o.textContent=Pt?Pt.emptyScript:"";for(let i=0;i<e;i++)o.append(t[i],Bt()),oe.nextNode(),a.push({type:2,index:++s});o.append(t[e],Bt())}}}else if(8===o.nodeType)if(o.data===Ft)a.push({type:2,index:s});else{let t=-1;for(;-1!==(t=o.data.indexOf(Ot,t+1));)a.push({type:7,index:s}),t+=Ot.length-1}s++}}static createElement(t,e){const i=Dt.createElement("template");return i.innerHTML=t,i}}function ae(t,e,i=t,o){if(e===te)return e;let s=void 0!==o?i._$Co?.[o]:i._$Cl;const r=Nt(e)?void 0:e._$litDirective$;return s?.constructor!==r&&(s?._$AO?.(!1),void 0===r?s=void 0:(s=new r(t),s._$AT(t,i,o)),void 0!==o?(i._$Co??=[])[o]=s:i._$Cl=s),void 0!==s&&(e=ae(t,s._$AS(t,e.values),s,o)),e}class le{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){const{el:{content:e},parts:i}=this._$AD,o=(t?.creationScope??Dt).importNode(e,!0);oe.currentNode=o;let s=oe.nextNode(),r=0,n=0,a=i[0];for(;void 0!==a;){if(r===a.index){let e;2===a.type?e=new ce(s,s.nextSibling,this,t):1===a.type?e=new a.ctor(s,a.name,a.strings,this,t):6===a.type&&(e=new be(s,this,t)),this._$AV.push(e),a=i[++n]}r!==a?.index&&(s=oe.nextNode(),r++)}return oe.currentNode=Dt,o}p(t){let e=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}}class ce{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,i,o){this.type=2,this._$AH=ee,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=o,this._$Cv=o?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t?.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=ae(this,t,e),Nt(t)?t===ee||null==t||""===t?(this._$AH!==ee&&this._$AR(),this._$AH=ee):t!==this._$AH&&t!==te&&this._(t):void 0!==t._$litType$?this.$(t):void 0!==t.nodeType?this.T(t):Ut(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==ee&&Nt(this._$AH)?this._$AA.nextSibling.data=t:this.T(Dt.createTextNode(t)),this._$AH=t}$(t){const{values:e,_$litType$:i}=t,o="number"==typeof i?this._$AC(t):(void 0===i.el&&(i.el=ne.createElement(se(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===o)this._$AH.p(e);else{const t=new le(o,this),i=t.u(this.options);t.p(e),this.T(i),this._$AH=t}}_$AC(t){let e=ie.get(t.strings);return void 0===e&&ie.set(t.strings,e=new ne(t)),e}k(t){Ht(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let i,o=0;for(const s of t)o===e.length?e.push(i=new ce(this.O(Bt()),this.O(Bt()),this,this.options)):i=e[o],i._$AI(s),o++;o<e.length&&(this._$AR(i&&i._$AB.nextSibling,o),e.length=o)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){void 0===this._$AM&&(this._$Cv=t,this._$AP?.(t))}}class de{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,i,o,s){this.type=1,this._$AH=ee,this._$AN=void 0,this.element=t,this.name=e,this._$AM=o,this.options=s,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=ee}_$AI(t,e=this,i,o){const s=this.strings;let r=!1;if(void 0===s)t=ae(this,t,e,0),r=!Nt(t)||t!==this._$AH&&t!==te,r&&(this._$AH=t);else{const o=t;let n,a;for(t=s[0],n=0;n<s.length-1;n++)a=ae(this,o[i+n],e,n),a===te&&(a=this._$AH[n]),r||=!Nt(a)||a!==this._$AH[n],a===ee?t=ee:t!==ee&&(t+=(a??"")+s[n+1]),this._$AH[n]=a}r&&!o&&this.j(t)}j(t){t===ee?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}}class he extends de{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===ee?void 0:t}}class ue extends de{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==ee)}}class pe extends de{constructor(t,e,i,o,s){super(t,e,i,o,s),this.type=5}_$AI(t,e=this){if((t=ae(this,t,e,0)??ee)===te)return;const i=this._$AH,o=t===ee&&i!==ee||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,s=t!==ee&&(i===ee||o);o&&this.element.removeEventListener(this.name,this,i),s&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}}class be{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){ae(this,t)}}const fe={M:Lt,P:Ot,A:Ft,C:1,L:re,R:le,D:Ut,V:ae,I:ce,H:de,N:ue,U:pe,B:he,F:be},me=zt.litHtmlPolyfillSupport;me?.(ne,ce),(zt.litHtmlVersions??=[]).push("3.3.1");const ge=globalThis;class ve extends Tt{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,i)=>{const o=i?.renderBefore??e;let s=o._$litPart$;if(void 0===s){const t=i?.renderBefore??null;o._$litPart$=s=new ce(e.insertBefore(Bt(),t),t,void 0,i??{})}return s._$AI(t),s})(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return te}}ve._$litElement$=!0,ve.finalized=!0,ge.litElementHydrateSupport?.({LitElement:ve});const ye=ge.litElementPolyfillSupport;ye?.({LitElement:ve}),(ge.litElementVersions??=[]).push("4.2.1");var we=pt`
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
`,_e=Object.defineProperty,xe=Object.defineProperties,$e=Object.getOwnPropertyDescriptor,ke=Object.getOwnPropertyDescriptors,Ae=Object.getOwnPropertySymbols,Ce=Object.prototype.hasOwnProperty,Ee=Object.prototype.propertyIsEnumerable,Se=(t,e)=>(e=Symbol[t])?e:Symbol.for("Symbol."+t),Te=t=>{throw TypeError(t)},ze=(t,e,i)=>e in t?_e(t,e,{enumerable:!0,configurable:!0,writable:!0,value:i}):t[e]=i,Pe=(t,e)=>{for(var i in e||(e={}))Ce.call(e,i)&&ze(t,i,e[i]);if(Ae)for(var i of Ae(e))Ee.call(e,i)&&ze(t,i,e[i]);return t},Ie=(t,e)=>xe(t,ke(e)),Le=(t,e,i,o)=>{for(var s,r=o>1?void 0:o?$e(e,i):e,n=t.length-1;n>=0;n--)(s=t[n])&&(r=(o?s(e,i,r):s(r))||r);return o&&r&&_e(e,i,r),r},Oe=(t,e,i)=>e.has(t)||Te("Cannot "+i),Fe=function(t,e){this[0]=t,this[1]=e};function Re(t,e){const i=Pe({waitUntilFirstUpdate:!1},e);return(e,o)=>{const{update:s}=e,r=Array.isArray(t)?t:[t];e.update=function(t){r.forEach(e=>{const s=e;if(t.has(s)){const e=t.get(s),r=this[s];e!==r&&(i.waitUntilFirstUpdate&&!this.hasUpdated||this[o](e,r))}}),s.call(this,t)}}}var De=pt`
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
`;const Be={attribute:!0,type:String,converter:Ct,reflect:!1,hasChanged:Et},Ne=(t=Be,e,i)=>{const{kind:o,metadata:s}=i;let r=globalThis.litPropertyMetadata.get(s);if(void 0===r&&globalThis.litPropertyMetadata.set(s,r=new Map),"setter"===o&&((t=Object.create(t)).wrapped=!0),r.set(i.name,t),"accessor"===o){const{name:o}=i;return{set(i){const s=e.get.call(this);e.set.call(this,i),this.requestUpdate(o,s,t)},init(e){return void 0!==e&&this.C(o,void 0,t,e),e}}}if("setter"===o){const{name:o}=i;return function(i){const s=this[o];e.call(this,i),this.requestUpdate(o,s,t)}}throw Error("Unsupported decorator location: "+o)};function He(t){return(e,i)=>"object"==typeof i?Ne(t,e,i):((t,e,i)=>{const o=e.hasOwnProperty(i);return e.constructor.createProperty(i,t),o?Object.getOwnPropertyDescriptor(e,i):void 0})(t,e,i)}function Ue(t){return He({...t,state:!0,attribute:!1})}const Me=(t,e,i)=>(i.configurable=!0,i.enumerable=!0,Reflect.decorate&&"object"!=typeof e&&Object.defineProperty(t,e,i),i);function Ve(t,e){return(i,o,s)=>{const r=e=>e.renderRoot?.querySelector(t)??null;if(e){const{get:t,set:e}="object"==typeof o?i:s??(()=>{const t=Symbol();return{get(){return this[t]},set(e){this[t]=e}}})();return Me(i,o,{get(){let i=t.call(this);return void 0===i&&(i=r(this),(null!==i||this.hasUpdated)&&e.call(this,i)),i}})}return Me(i,o,{get(){return r(this)}})}}var je,We=class extends ve{constructor(){var t,e;super(),t=this,(e=je).has(t)?Te("Cannot add the same private member more than once"):e instanceof WeakSet?e.add(t):e.set(t,false),this.initialReflectedProperties=new Map,Object.entries(this.constructor.dependencies).forEach(([t,e])=>{this.constructor.define(t,e)})}emit(t,e){const i=new CustomEvent(t,Pe({bubbles:!0,cancelable:!1,composed:!0,detail:{}},e));return this.dispatchEvent(i),i}static define(t,e=this,i={}){const o=customElements.get(t);if(!o){try{customElements.define(t,e,i)}catch(o){customElements.define(t,class extends e{},i)}return}let s=" (unknown version)",r=s;"version"in e&&e.version&&(s=" v"+e.version),"version"in o&&o.version&&(r=" v"+o.version),s&&r&&s===r||console.warn(`Attempted to register <${t}>${s}, but <${t}>${r} has already been registered.`)}attributeChangedCallback(t,e,i){var o;Oe(this,o=je,"read from private field"),o.get(this)||(this.constructor.elementProperties.forEach((t,e)=>{t.reflect&&null!=this[e]&&this.initialReflectedProperties.set(e,this[e])}),((t,e,i)=>{Oe(t,e,"write to private field"),e.set(t,i)})(this,je,!0)),super.attributeChangedCallback(t,e,i)}willUpdate(t){super.willUpdate(t),this.initialReflectedProperties.forEach((e,i)=>{t.has(i)&&null==this[i]&&(this[i]=e)})}};je=new WeakMap,We.version="2.20.1",We.dependencies={},Le([He()],We.prototype,"dir",2),Le([He()],We.prototype,"lang",2);var qe=class extends We{constructor(){super(...arguments),this.vertical=!1}connectedCallback(){super.connectedCallback(),this.setAttribute("role","separator")}handleVerticalChange(){this.setAttribute("aria-orientation",this.vertical?"vertical":"horizontal")}};function*Ke(t=document.activeElement){var e,i,o,s,r;null!=t&&(yield t,"shadowRoot"in t&&t.shadowRoot&&"closed"!==t.shadowRoot.mode&&(yield*(e=Ke(t.shadowRoot.activeElement),o=e[Se("asyncIterator")],s=!1,r={},null==o?(o=e[Se("iterator")](),i=t=>r[t]=e=>o[t](e)):(o=o.call(e),i=t=>r[t]=e=>{if(s){if(s=!1,"throw"===t)throw e;return e}return s=!0,{done:!1,value:new Fe(new Promise(i=>{var s=o[t](e);s instanceof Object||Te("Object expected"),i(s)}),1)}}),r[Se("iterator")]=()=>r,i("next"),"throw"in o?i("throw"):r.throw=t=>{throw t},"return"in o&&i("return"),r)))}qe.styles=[De,we],Le([He({type:Boolean,reflect:!0})],qe.prototype,"vertical",2),Le([Re("vertical")],qe.prototype,"handleVerticalChange",1),qe.define("sl-divider");var Ge=new WeakMap;function Ze(t){let e=Ge.get(t);return e||(e=window.getComputedStyle(t,null),Ge.set(t,e)),e}function Ye(t){const e=new WeakMap,i=[];return function o(s){if(s instanceof Element){if(s.hasAttribute("inert")||s.closest("[inert]"))return;if(e.has(s))return;e.set(s,!0),!i.includes(s)&&function(t){const e=t.tagName.toLowerCase(),i=Number(t.getAttribute("tabindex"));if(t.hasAttribute("tabindex")&&(isNaN(i)||i<=-1))return!1;if(t.hasAttribute("disabled"))return!1;if(t.closest("[inert]"))return!1;if("input"===e&&"radio"===t.getAttribute("type")){const e=t.getRootNode(),i=`input[type='radio'][name="${t.getAttribute("name")}"]`,o=e.querySelector(`${i}:checked`);return o?o===t:e.querySelector(i)===t}return!!function(t){if("function"==typeof t.checkVisibility)return t.checkVisibility({checkOpacity:!1,checkVisibilityCSS:!0});const e=Ze(t);return"hidden"!==e.visibility&&"none"!==e.display}(t)&&(!("audio"!==e&&"video"!==e||!t.hasAttribute("controls"))||!!t.hasAttribute("tabindex")||!(!t.hasAttribute("contenteditable")||"false"===t.getAttribute("contenteditable"))||!!["button","input","select","textarea","a","audio","video","summary","iframe"].includes(e)||function(t){const e=Ze(t),{overflowY:i,overflowX:o}=e;return"scroll"===i||"scroll"===o||"auto"===i&&"auto"===o&&(t.scrollHeight>t.clientHeight&&"auto"===i||!(!(t.scrollWidth>t.clientWidth)||"auto"!==o))}(t))}(s)&&i.push(s),s instanceof HTMLSlotElement&&function(t,e){var i;return(null==(i=t.getRootNode({composed:!0}))?void 0:i.host)!==e}(s,t)&&s.assignedElements({flatten:!0}).forEach(t=>{o(t)}),null!==s.shadowRoot&&"open"===s.shadowRoot.mode&&o(s.shadowRoot)}for(const t of s.children)o(t)}(t),i.sort((t,e)=>{const i=Number(t.getAttribute("tabindex"))||0;return(Number(e.getAttribute("tabindex"))||0)-i})}var Xe=[],Je=class{constructor(t){this.tabDirection="forward",this.handleFocusIn=()=>{this.isActive()&&this.checkFocus()},this.handleKeyDown=t=>{var e;if("Tab"!==t.key||this.isExternalActivated)return;if(!this.isActive())return;const i=[...Ke()].pop();if(this.previousFocus=i,this.previousFocus&&this.possiblyHasTabbableChildren(this.previousFocus))return;t.shiftKey?this.tabDirection="backward":this.tabDirection="forward";const o=Ye(this.element);let s=o.findIndex(t=>t===i);this.previousFocus=this.currentFocus;const r="forward"===this.tabDirection?1:-1;for(;;){s+r>=o.length?s=0:s+r<0?s=o.length-1:s+=r,this.previousFocus=this.currentFocus;const i=o[s];if("backward"===this.tabDirection&&this.previousFocus&&this.possiblyHasTabbableChildren(this.previousFocus))return;if(i&&this.possiblyHasTabbableChildren(i))return;t.preventDefault(),this.currentFocus=i,null==(e=this.currentFocus)||e.focus({preventScroll:!1});const n=[...Ke()];if(n.includes(this.currentFocus)||!n.includes(this.previousFocus))break}setTimeout(()=>this.checkFocus())},this.handleKeyUp=()=>{this.tabDirection="forward"},this.element=t,this.elementsWithTabbableControls=["iframe"]}activate(){Xe.push(this.element),document.addEventListener("focusin",this.handleFocusIn),document.addEventListener("keydown",this.handleKeyDown),document.addEventListener("keyup",this.handleKeyUp)}deactivate(){Xe=Xe.filter(t=>t!==this.element),this.currentFocus=null,document.removeEventListener("focusin",this.handleFocusIn),document.removeEventListener("keydown",this.handleKeyDown),document.removeEventListener("keyup",this.handleKeyUp)}isActive(){return Xe[Xe.length-1]===this.element}activateExternal(){this.isExternalActivated=!0}deactivateExternal(){this.isExternalActivated=!1}checkFocus(){if(this.isActive()&&!this.isExternalActivated){const t=Ye(this.element);if(!this.element.matches(":focus-within")){const e=t[0],i=t[t.length-1],o="forward"===this.tabDirection?e:i;"function"==typeof(null==o?void 0:o.focus)&&(this.currentFocus=o,o.focus({preventScroll:!1}))}}}possiblyHasTabbableChildren(t){return this.elementsWithTabbableControls.includes(t.tagName.toLowerCase())||t.hasAttribute("controls")}},Qe=new Set;function ti(t){if(Qe.add(t),!document.documentElement.classList.contains("sl-scroll-lock")){const t=function(){const t=document.documentElement.clientWidth;return Math.abs(window.innerWidth-t)}()+function(){const t=Number(getComputedStyle(document.body).paddingRight.replace(/px/,""));return isNaN(t)||!t?0:t}();let e=getComputedStyle(document.documentElement).scrollbarGutter;e&&"auto"!==e||(e="stable"),t<2&&(e=""),document.documentElement.style.setProperty("--sl-scroll-lock-gutter",e),document.documentElement.classList.add("sl-scroll-lock"),document.documentElement.style.setProperty("--sl-scroll-lock-size",`${t}px`)}}function ei(t){Qe.delete(t),0===Qe.size&&(document.documentElement.classList.remove("sl-scroll-lock"),document.documentElement.style.removeProperty("--sl-scroll-lock-size"))}function ii(t,e,i="vertical",o="smooth"){const s=function(t,e){return{top:Math.round(t.getBoundingClientRect().top-e.getBoundingClientRect().top),left:Math.round(t.getBoundingClientRect().left-e.getBoundingClientRect().left)}}(t,e),r=s.top+e.scrollTop,n=s.left+e.scrollLeft,a=e.scrollLeft,l=e.scrollLeft+e.offsetWidth,c=e.scrollTop,d=e.scrollTop+e.offsetHeight;"horizontal"!==i&&"both"!==i||(n<a?e.scrollTo({left:n,behavior:o}):n+t.clientWidth>l&&e.scrollTo({left:n-e.offsetWidth+t.clientWidth,behavior:o})),"vertical"!==i&&"both"!==i||(r<c?e.scrollTo({top:r,behavior:o}):r+t.clientHeight>d&&e.scrollTo({top:r-e.offsetHeight+t.clientHeight,behavior:o}))}var oi=pt`
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
`,si=t=>{var e;const{activeElement:i}=document;i&&t.contains(i)&&(null==(e=document.activeElement)||e.blur())},ri=pt`
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
`,ni="";function ai(t){ni=t}var li={name:"default",resolver:t=>function(t=""){if(!ni){const t=[...document.getElementsByTagName("script")],e=t.find(t=>t.hasAttribute("data-shoelace"));if(e)ai(e.getAttribute("data-shoelace"));else{const e=t.find(t=>/shoelace(\.min)?\.js($|\?)/.test(t.src)||/shoelace-autoloader(\.min)?\.js($|\?)/.test(t.src));let i="";e&&(i=e.getAttribute("src")),ai(i.split("/").slice(0,-1).join("/"))}}return ni.replace(/\/$/,"")+(t?`/${t.replace(/^\//,"")}`:"")}(`assets/icons/${t}.svg`)},ci={caret:'\n    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">\n      <polyline points="6 9 12 15 18 9"></polyline>\n    </svg>\n  ',check:'\n    <svg part="checked-icon" class="checkbox__icon" viewBox="0 0 16 16">\n      <g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd" stroke-linecap="round">\n        <g stroke="currentColor">\n          <g transform="translate(3.428571, 3.428571)">\n            <path d="M0,5.71428571 L3.42857143,9.14285714"></path>\n            <path d="M9.14285714,0 L3.42857143,9.14285714"></path>\n          </g>\n        </g>\n      </g>\n    </svg>\n  ',"chevron-down":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-down" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',"chevron-left":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-left" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0z"/>\n    </svg>\n  ',"chevron-right":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-right" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z"/>\n    </svg>\n  ',copy:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-copy" viewBox="0 0 16 16">\n      <path fill-rule="evenodd" d="M4 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V2Zm2-1a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H6ZM2 5a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1v-1h1v1a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h1v1H2Z"/>\n    </svg>\n  ',eye:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye" viewBox="0 0 16 16">\n      <path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8zM1.173 8a13.133 13.133 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.133 13.133 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5c-2.12 0-3.879-1.168-5.168-2.457A13.134 13.134 0 0 1 1.172 8z"/>\n      <path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0z"/>\n    </svg>\n  ',"eye-slash":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye-slash" viewBox="0 0 16 16">\n      <path d="M13.359 11.238C15.06 9.72 16 8 16 8s-3-5.5-8-5.5a7.028 7.028 0 0 0-2.79.588l.77.771A5.944 5.944 0 0 1 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.134 13.134 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755-.165.165-.337.328-.517.486l.708.709z"/>\n      <path d="M11.297 9.176a3.5 3.5 0 0 0-4.474-4.474l.823.823a2.5 2.5 0 0 1 2.829 2.829l.822.822zm-2.943 1.299.822.822a3.5 3.5 0 0 1-4.474-4.474l.823.823a2.5 2.5 0 0 0 2.829 2.829z"/>\n      <path d="M3.35 5.47c-.18.16-.353.322-.518.487A13.134 13.134 0 0 0 1.172 8l.195.288c.335.48.83 1.12 1.465 1.755C4.121 11.332 5.881 12.5 8 12.5c.716 0 1.39-.133 2.02-.36l.77.772A7.029 7.029 0 0 1 8 13.5C3 13.5 0 8 0 8s.939-1.721 2.641-3.238l.708.709zm10.296 8.884-12-12 .708-.708 12 12-.708.708z"/>\n    </svg>\n  ',eyedropper:'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eyedropper" viewBox="0 0 16 16">\n      <path d="M13.354.646a1.207 1.207 0 0 0-1.708 0L8.5 3.793l-.646-.647a.5.5 0 1 0-.708.708L8.293 5l-7.147 7.146A.5.5 0 0 0 1 12.5v1.793l-.854.853a.5.5 0 1 0 .708.707L1.707 15H3.5a.5.5 0 0 0 .354-.146L11 7.707l1.146 1.147a.5.5 0 0 0 .708-.708l-.647-.646 3.147-3.146a1.207 1.207 0 0 0 0-1.708l-2-2zM2 12.707l7-7L10.293 7l-7 7H2v-1.293z"></path>\n    </svg>\n  ',"grip-vertical":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-grip-vertical" viewBox="0 0 16 16">\n      <path d="M7 2a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zM7 5a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zM7 8a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm-3 3a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm-3 3a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"></path>\n    </svg>\n  ',indeterminate:'\n    <svg part="indeterminate-icon" class="checkbox__icon" viewBox="0 0 16 16">\n      <g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd" stroke-linecap="round">\n        <g stroke="currentColor" stroke-width="2">\n          <g transform="translate(2.285714, 6.857143)">\n            <path d="M10.2857143,1.14285714 L1.14285714,1.14285714"></path>\n          </g>\n        </g>\n      </g>\n    </svg>\n  ',"person-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-fill" viewBox="0 0 16 16">\n      <path d="M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H3zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/>\n    </svg>\n  ',"play-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-play-fill" viewBox="0 0 16 16">\n      <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"></path>\n    </svg>\n  ',"pause-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pause-fill" viewBox="0 0 16 16">\n      <path d="M5.5 3.5A1.5 1.5 0 0 1 7 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5zm5 0A1.5 1.5 0 0 1 12 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5z"></path>\n    </svg>\n  ',radio:'\n    <svg part="checked-icon" class="radio__icon" viewBox="0 0 16 16">\n      <g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">\n        <g fill="currentColor">\n          <circle cx="8" cy="8" r="3.42857143"></circle>\n        </g>\n      </g>\n    </svg>\n  ',"star-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-star-fill" viewBox="0 0 16 16">\n      <path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/>\n    </svg>\n  ',"x-lg":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-lg" viewBox="0 0 16 16">\n      <path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8 2.146 2.854Z"/>\n    </svg>\n  ',"x-circle-fill":'\n    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-circle-fill" viewBox="0 0 16 16">\n      <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"></path>\n    </svg>\n  '},di=[li,{name:"system",resolver:t=>t in ci?`data:image/svg+xml,${encodeURIComponent(ci[t])}`:""}],hi=[];function ui(t){return di.find(e=>e.name===t)}var pi=pt`
  :host {
    display: inline-block;
    width: 1em;
    height: 1em;
    box-sizing: content-box !important;
  }

  svg {
    display: block;
    height: 100%;
    width: 100%;
  }
`;const{I:bi}=fe,fi={};var mi,gi=Symbol(),vi=Symbol(),yi=new Map,wi=class extends We{constructor(){super(...arguments),this.initialRender=!1,this.svg=null,this.label="",this.library="default"}async resolveIcon(t,e){var i;let o;if(null==e?void 0:e.spriteSheet)return this.svg=Xt`<svg part="svg">
        <use part="use" href="${t}"></use>
      </svg>`,this.svg;try{if(o=await fetch(t,{mode:"cors"}),!o.ok)return 410===o.status?gi:vi}catch(t){return vi}try{const t=document.createElement("div");t.innerHTML=await o.text();const e=t.firstElementChild;if("svg"!==(null==(i=null==e?void 0:e.tagName)?void 0:i.toLowerCase()))return gi;mi||(mi=new DOMParser);const s=mi.parseFromString(e.outerHTML,"text/html").body.querySelector("svg");return s?(s.part.add("svg"),document.adoptNode(s)):gi}catch(t){return gi}}connectedCallback(){super.connectedCallback(),hi.push(this)}firstUpdated(){this.initialRender=!0,this.setIcon()}disconnectedCallback(){var t;super.disconnectedCallback(),t=this,hi=hi.filter(e=>e!==t)}getIconSource(){const t=ui(this.library);return this.name&&t?{url:t.resolver(this.name),fromLibrary:!0}:{url:this.src,fromLibrary:!1}}handleLabelChange(){"string"==typeof this.label&&this.label.length>0?(this.setAttribute("role","img"),this.setAttribute("aria-label",this.label),this.removeAttribute("aria-hidden")):(this.removeAttribute("role"),this.removeAttribute("aria-label"),this.setAttribute("aria-hidden","true"))}async setIcon(){var t;const{url:e,fromLibrary:i}=this.getIconSource(),o=i?ui(this.library):void 0;if(!e)return void(this.svg=null);let s=yi.get(e);if(s||(s=this.resolveIcon(e,o),yi.set(e,s)),!this.initialRender)return;const r=await s;if(r===vi&&yi.delete(e),e===this.getIconSource().url)if((t=>void 0!==t?._$litType$)(r)){if(this.svg=r,o){await this.updateComplete;const t=this.shadowRoot.querySelector("[part='svg']");"function"==typeof o.mutator&&t&&o.mutator(t)}}else switch(r){case vi:case gi:this.svg=null,this.emit("sl-error");break;default:this.svg=r.cloneNode(!0),null==(t=null==o?void 0:o.mutator)||t.call(o,this.svg),this.emit("sl-load")}}render(){return this.svg}};wi.styles=[De,pi],Le([Ue()],wi.prototype,"svg",2),Le([He({reflect:!0})],wi.prototype,"name",2),Le([He()],wi.prototype,"src",2),Le([He()],wi.prototype,"label",2),Le([He({reflect:!0})],wi.prototype,"library",2),Le([Re("label")],wi.prototype,"handleLabelChange",1),Le([Re(["name","src","library"])],wi.prototype,"setIcon",1);const _i=t=>(...e)=>({_$litDirective$:t,values:e});class xi{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,i){this._$Ct=t,this._$AM=e,this._$Ci=i}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}}const $i=_i(class extends xi{constructor(t){if(super(t),1!==t.type||"class"!==t.name||t.strings?.length>2)throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(t){return" "+Object.keys(t).filter(e=>t[e]).join(" ")+" "}update(t,[e]){if(void 0===this.st){this.st=new Set,void 0!==t.strings&&(this.nt=new Set(t.strings.join(" ").split(/\s/).filter(t=>""!==t)));for(const t in e)e[t]&&!this.nt?.has(t)&&this.st.add(t);return this.render(e)}const i=t.element.classList;for(const t of this.st)t in e||(i.remove(t),this.st.delete(t));for(const t in e){const o=!!e[t];o===this.st.has(t)||this.nt?.has(t)||(o?(i.add(t),this.st.add(t)):(i.remove(t),this.st.delete(t)))}return te}}),ki=Symbol.for(""),Ai=t=>{if(t?.r===ki)return t?._$litStatic$},Ci=(t,...e)=>({_$litStatic$:e.reduce((e,i,o)=>e+(t=>{if(void 0!==t._$litStatic$)return t._$litStatic$;throw Error(`Value passed to 'literal' function must be a 'literal' result: ${t}. Use 'unsafeStatic' to pass non-literal values, but\n            take care to ensure page security.`)})(i)+t[o+1],t[0]),r:ki}),Ei=new Map,Si=t=>(e,...i)=>{const o=i.length;let s,r;const n=[],a=[];let l,c=0,d=!1;for(;c<o;){for(l=e[c];c<o&&void 0!==(r=i[c],s=Ai(r));)l+=s+e[++c],d=!0;c!==o&&a.push(r),n.push(l),c++}if(c===o&&n.push(e[o]),d){const t=n.join("$$lit$$");void 0===(e=Ei.get(t))&&(n.raw=n,Ei.set(t,e=n)),i=a}return t(e,...i)},Ti=Si(Xt),zi=(Si(Jt),Si(Qt),t=>t??ee);var Pi=class extends We{constructor(){super(...arguments),this.hasFocus=!1,this.label="",this.disabled=!1}handleBlur(){this.hasFocus=!1,this.emit("sl-blur")}handleFocus(){this.hasFocus=!0,this.emit("sl-focus")}handleClick(t){this.disabled&&(t.preventDefault(),t.stopPropagation())}click(){this.button.click()}focus(t){this.button.focus(t)}blur(){this.button.blur()}render(){const t=!!this.href,e=t?Ci`a`:Ci`button`;return Ti`
      <${e}
        part="base"
        class=${$i({"icon-button":!0,"icon-button--disabled":!t&&this.disabled,"icon-button--focused":this.hasFocus})}
        ?disabled=${zi(t?void 0:this.disabled)}
        type=${zi(t?void 0:"button")}
        href=${zi(t?this.href:void 0)}
        target=${zi(t?this.target:void 0)}
        download=${zi(t?this.download:void 0)}
        rel=${zi(t&&this.target?"noreferrer noopener":void 0)}
        role=${zi(t?void 0:"button")}
        aria-disabled=${this.disabled?"true":"false"}
        aria-label="${this.label}"
        tabindex=${this.disabled?"-1":"0"}
        @blur=${this.handleBlur}
        @focus=${this.handleFocus}
        @click=${this.handleClick}
      >
        <sl-icon
          class="icon-button__icon"
          name=${zi(this.name)}
          library=${zi(this.library)}
          src=${zi(this.src)}
          aria-hidden="true"
        ></sl-icon>
      </${e}>
    `}};Pi.styles=[De,ri],Pi.dependencies={"sl-icon":wi},Le([Ve(".icon-button")],Pi.prototype,"button",2),Le([Ue()],Pi.prototype,"hasFocus",2),Le([He()],Pi.prototype,"name",2),Le([He()],Pi.prototype,"library",2),Le([He()],Pi.prototype,"src",2),Le([He()],Pi.prototype,"href",2),Le([He()],Pi.prototype,"target",2),Le([He()],Pi.prototype,"download",2),Le([He()],Pi.prototype,"label",2),Le([He({type:Boolean,reflect:!0})],Pi.prototype,"disabled",2);var Ii=new Map,Li=new WeakMap;function Oi(t,e){return"rtl"===e.toLowerCase()?{keyframes:t.rtlKeyframes||t.keyframes,options:t.options}:t}function Fi(t,e){Ii.set(t,function(t){return null!=t?t:{keyframes:[],options:{duration:0}}}(e))}function Ri(t,e,i){const o=Li.get(t);if(null==o?void 0:o[e])return Oi(o[e],i.dir);const s=Ii.get(e);return s?Oi(s,i.dir):{keyframes:[],options:{duration:0}}}function Di(t,e){return new Promise(i=>{t.addEventListener(e,function o(s){s.target===t&&(t.removeEventListener(e,o),i())})})}function Bi(t,e,i){return new Promise(o=>{if((null==i?void 0:i.duration)===1/0)throw new Error("Promise-based animations must be finite.");const s=t.animate(e,Ie(Pe({},i),{duration:window.matchMedia("(prefers-reduced-motion: reduce)").matches?0:i.duration}));s.addEventListener("cancel",o,{once:!0}),s.addEventListener("finish",o,{once:!0})})}function Ni(t){return(t=t.toString().toLowerCase()).indexOf("ms")>-1?parseFloat(t):t.indexOf("s")>-1?1e3*parseFloat(t):parseFloat(t)}function Hi(t){return Promise.all(t.getAnimations().map(t=>new Promise(e=>{t.cancel(),requestAnimationFrame(e)})))}function Ui(t,e){return t.map(t=>Ie(Pe({},t),{height:"auto"===t.height?`${e}px`:t.height}))}var Mi=class{constructor(t,...e){this.slotNames=[],this.handleSlotChange=t=>{const e=t.target;(this.slotNames.includes("[default]")&&!e.name||e.name&&this.slotNames.includes(e.name))&&this.host.requestUpdate()},(this.host=t).addController(this),this.slotNames=e}hasDefaultSlot(){return[...this.host.childNodes].some(t=>{if(t.nodeType===t.TEXT_NODE&&""!==t.textContent.trim())return!0;if(t.nodeType===t.ELEMENT_NODE){const e=t;if("sl-visually-hidden"===e.tagName.toLowerCase())return!1;if(!e.hasAttribute("slot"))return!0}return!1})}hasNamedSlot(t){return null!==this.host.querySelector(`:scope > [slot="${t}"]`)}test(t){return"[default]"===t?this.hasDefaultSlot():this.hasNamedSlot(t)}hostConnected(){this.host.shadowRoot.addEventListener("slotchange",this.handleSlotChange)}hostDisconnected(){this.host.shadowRoot.removeEventListener("slotchange",this.handleSlotChange)}};const Vi=new Set,ji=new Map;let Wi,qi="ltr",Ki="en";const Gi="undefined"!=typeof MutationObserver&&"undefined"!=typeof document&&void 0!==document.documentElement;if(Gi){const t=new MutationObserver(Yi);qi=document.documentElement.dir||"ltr",Ki=document.documentElement.lang||navigator.language,t.observe(document.documentElement,{attributes:!0,attributeFilter:["dir","lang"]})}function Zi(...t){t.map(t=>{const e=t.$code.toLowerCase();ji.has(e)?ji.set(e,Object.assign(Object.assign({},ji.get(e)),t)):ji.set(e,t),Wi||(Wi=t)}),Yi()}function Yi(){Gi&&(qi=document.documentElement.dir||"ltr",Ki=document.documentElement.lang||navigator.language),[...Vi.keys()].map(t=>{"function"==typeof t.requestUpdate&&t.requestUpdate()})}class Xi{constructor(t){this.host=t,this.host.addController(this)}hostConnected(){Vi.add(this.host)}hostDisconnected(){Vi.delete(this.host)}dir(){return`${this.host.dir||qi}`.toLowerCase()}lang(){return`${this.host.lang||Ki}`.toLowerCase()}getTranslationData(t){var e,i;const o=new Intl.Locale(t.replace(/_/g,"-")),s=null==o?void 0:o.language.toLowerCase(),r=null!==(i=null===(e=null==o?void 0:o.region)||void 0===e?void 0:e.toLowerCase())&&void 0!==i?i:"";return{locale:o,language:s,region:r,primary:ji.get(`${s}-${r}`),secondary:ji.get(s)}}exists(t,e){var i;const{primary:o,secondary:s}=this.getTranslationData(null!==(i=e.lang)&&void 0!==i?i:this.lang());return e=Object.assign({includeFallback:!1},e),!!(o&&o[t]||s&&s[t]||e.includeFallback&&Wi&&Wi[t])}term(t,...e){const{primary:i,secondary:o}=this.getTranslationData(this.lang());let s;if(i&&i[t])s=i[t];else if(o&&o[t])s=o[t];else{if(!Wi||!Wi[t])return console.error(`No translation found for: ${String(t)}`),String(t);s=Wi[t]}return"function"==typeof s?s(...e):s}date(t,e){return t=new Date(t),new Intl.DateTimeFormat(this.lang(),e).format(t)}number(t,e){return t=Number(t),isNaN(t)?"":new Intl.NumberFormat(this.lang(),e).format(t)}relativeTime(t,e,i){return new Intl.RelativeTimeFormat(this.lang(),i).format(t,e)}}var Ji={$code:"en",$name:"English",$dir:"ltr",carousel:"Carousel",clearEntry:"Clear entry",close:"Close",copied:"Copied",copy:"Copy",currentValue:"Current value",error:"Error",goToSlide:(t,e)=>`Go to slide ${t} of ${e}`,hidePassword:"Hide password",loading:"Loading",nextSlide:"Next slide",numOptionsSelected:t=>0===t?"No options selected":1===t?"1 option selected":`${t} options selected`,previousSlide:"Previous slide",progress:"Progress",remove:"Remove",resize:"Resize",scrollToEnd:"Scroll to end",scrollToStart:"Scroll to start",selectAColorFromTheScreen:"Select a color from the screen",showPassword:"Show password",slideNum:t=>`Slide ${t}`,toggleColorFormat:"Toggle color format"};Zi(Ji);var Qi=Ji,to=class extends Xi{};Zi(Qi);var eo=class extends We{constructor(){super(...arguments),this.hasSlotController=new Mi(this,"footer"),this.localize=new to(this),this.modal=new Je(this),this.open=!1,this.label="",this.noHeader=!1,this.handleDocumentKeyDown=t=>{"Escape"===t.key&&this.modal.isActive()&&this.open&&(t.stopPropagation(),this.requestClose("keyboard"))}}firstUpdated(){this.dialog.hidden=!this.open,this.open&&(this.addOpenListeners(),this.modal.activate(),ti(this))}disconnectedCallback(){super.disconnectedCallback(),this.modal.deactivate(),ei(this),this.removeOpenListeners()}requestClose(t){if(this.emit("sl-request-close",{cancelable:!0,detail:{source:t}}).defaultPrevented){const t=Ri(this,"dialog.denyClose",{dir:this.localize.dir()});return void Bi(this.panel,t.keyframes,t.options)}this.hide()}addOpenListeners(){var t;"CloseWatcher"in window?(null==(t=this.closeWatcher)||t.destroy(),this.closeWatcher=new CloseWatcher,this.closeWatcher.onclose=()=>this.requestClose("keyboard")):document.addEventListener("keydown",this.handleDocumentKeyDown)}removeOpenListeners(){var t;null==(t=this.closeWatcher)||t.destroy(),document.removeEventListener("keydown",this.handleDocumentKeyDown)}async handleOpenChange(){if(this.open){this.emit("sl-show"),this.addOpenListeners(),this.originalTrigger=document.activeElement,this.modal.activate(),ti(this);const t=this.querySelector("[autofocus]");t&&t.removeAttribute("autofocus"),await Promise.all([Hi(this.dialog),Hi(this.overlay)]),this.dialog.hidden=!1,requestAnimationFrame(()=>{this.emit("sl-initial-focus",{cancelable:!0}).defaultPrevented||(t?t.focus({preventScroll:!0}):this.panel.focus({preventScroll:!0})),t&&t.setAttribute("autofocus","")});const e=Ri(this,"dialog.show",{dir:this.localize.dir()}),i=Ri(this,"dialog.overlay.show",{dir:this.localize.dir()});await Promise.all([Bi(this.panel,e.keyframes,e.options),Bi(this.overlay,i.keyframes,i.options)]),this.emit("sl-after-show")}else{si(this),this.emit("sl-hide"),this.removeOpenListeners(),this.modal.deactivate(),await Promise.all([Hi(this.dialog),Hi(this.overlay)]);const t=Ri(this,"dialog.hide",{dir:this.localize.dir()}),e=Ri(this,"dialog.overlay.hide",{dir:this.localize.dir()});await Promise.all([Bi(this.overlay,e.keyframes,e.options).then(()=>{this.overlay.hidden=!0}),Bi(this.panel,t.keyframes,t.options).then(()=>{this.panel.hidden=!0})]),this.dialog.hidden=!0,this.overlay.hidden=!1,this.panel.hidden=!1,ei(this);const i=this.originalTrigger;"function"==typeof(null==i?void 0:i.focus)&&setTimeout(()=>i.focus()),this.emit("sl-after-hide")}}async show(){if(!this.open)return this.open=!0,Di(this,"sl-after-show")}async hide(){if(this.open)return this.open=!1,Di(this,"sl-after-hide")}render(){return Xt`
      <div
        part="base"
        class=${$i({dialog:!0,"dialog--open":this.open,"dialog--has-footer":this.hasSlotController.test("footer")})}
      >
        <div part="overlay" class="dialog__overlay" @click=${()=>this.requestClose("overlay")} tabindex="-1"></div>

        <div
          part="panel"
          class="dialog__panel"
          role="dialog"
          aria-modal="true"
          aria-hidden=${this.open?"false":"true"}
          aria-label=${zi(this.noHeader?this.label:void 0)}
          aria-labelledby=${zi(this.noHeader?void 0:"title")}
          tabindex="-1"
        >
          ${this.noHeader?"":Xt`
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
          ${""}
          <div part="body" class="dialog__body" tabindex="-1"><slot></slot></div>

          <footer part="footer" class="dialog__footer">
            <slot name="footer"></slot>
          </footer>
        </div>
      </div>
    `}};eo.styles=[De,oi],eo.dependencies={"sl-icon-button":Pi},Le([Ve(".dialog")],eo.prototype,"dialog",2),Le([Ve(".dialog__panel")],eo.prototype,"panel",2),Le([Ve(".dialog__overlay")],eo.prototype,"overlay",2),Le([He({type:Boolean,reflect:!0})],eo.prototype,"open",2),Le([He({reflect:!0})],eo.prototype,"label",2),Le([He({attribute:"no-header",type:Boolean,reflect:!0})],eo.prototype,"noHeader",2),Le([Re("open",{waitUntilFirstUpdate:!0})],eo.prototype,"handleOpenChange",1),Fi("dialog.show",{keyframes:[{opacity:0,scale:.8},{opacity:1,scale:1}],options:{duration:250,easing:"ease"}}),Fi("dialog.hide",{keyframes:[{opacity:1,scale:1},{opacity:0,scale:.8}],options:{duration:250,easing:"ease"}}),Fi("dialog.denyClose",{keyframes:[{scale:1},{scale:1.02},{scale:1}],options:{duration:250}}),Fi("dialog.overlay.show",{keyframes:[{opacity:0},{opacity:1}],options:{duration:250}}),Fi("dialog.overlay.hide",{keyframes:[{opacity:1},{opacity:0}],options:{duration:250}}),eo.define("sl-dialog");var io=pt`
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
    text-align: start;
    white-space: normal;
    color: var(--sl-tooltip-color);
    padding: var(--sl-tooltip-padding);
    pointer-events: none;
    user-select: none;
    -webkit-user-select: none;
  }
`,oo=pt`
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

  /* Hover bridge */
  .popup-hover-bridge:not(.popup-hover-bridge--visible) {
    display: none;
  }

  .popup-hover-bridge {
    position: fixed;
    z-index: calc(var(--sl-z-index-dropdown) - 1);
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    clip-path: polygon(
      var(--hover-bridge-top-left-x, 0) var(--hover-bridge-top-left-y, 0),
      var(--hover-bridge-top-right-x, 0) var(--hover-bridge-top-right-y, 0),
      var(--hover-bridge-bottom-right-x, 0) var(--hover-bridge-bottom-right-y, 0),
      var(--hover-bridge-bottom-left-x, 0) var(--hover-bridge-bottom-left-y, 0)
    );
  }
`;const so=Math.min,ro=Math.max,no=Math.round,ao=Math.floor,lo=t=>({x:t,y:t}),co={left:"right",right:"left",bottom:"top",top:"bottom"},ho={start:"end",end:"start"};function uo(t,e,i){return ro(t,so(e,i))}function po(t,e){return"function"==typeof t?t(e):t}function bo(t){return t.split("-")[0]}function fo(t){return t.split("-")[1]}function mo(t){return"x"===t?"y":"x"}function go(t){return"y"===t?"height":"width"}const vo=new Set(["top","bottom"]);function yo(t){return vo.has(bo(t))?"y":"x"}function wo(t){return mo(yo(t))}function _o(t){return t.replace(/start|end/g,t=>ho[t])}const xo=["left","right"],$o=["right","left"],ko=["top","bottom"],Ao=["bottom","top"];function Co(t){return t.replace(/left|right|bottom|top/g,t=>co[t])}function Eo(t){return"number"!=typeof t?function(t){return{top:0,right:0,bottom:0,left:0,...t}}(t):{top:t,right:t,bottom:t,left:t}}function So(t){const{x:e,y:i,width:o,height:s}=t;return{width:o,height:s,top:i,left:e,right:e+o,bottom:i+s,x:e,y:i}}function To(t,e,i){let{reference:o,floating:s}=t;const r=yo(e),n=wo(e),a=go(n),l=bo(e),c="y"===r,d=o.x+o.width/2-s.width/2,h=o.y+o.height/2-s.height/2,u=o[a]/2-s[a]/2;let p;switch(l){case"top":p={x:d,y:o.y-s.height};break;case"bottom":p={x:d,y:o.y+o.height};break;case"right":p={x:o.x+o.width,y:h};break;case"left":p={x:o.x-s.width,y:h};break;default:p={x:o.x,y:o.y}}switch(fo(e)){case"start":p[n]-=u*(i&&c?-1:1);break;case"end":p[n]+=u*(i&&c?-1:1)}return p}async function zo(t,e){var i;void 0===e&&(e={});const{x:o,y:s,platform:r,rects:n,elements:a,strategy:l}=t,{boundary:c="clippingAncestors",rootBoundary:d="viewport",elementContext:h="floating",altBoundary:u=!1,padding:p=0}=po(e,t),b=Eo(p),f=a[u?"floating"===h?"reference":"floating":h],m=So(await r.getClippingRect({element:null==(i=await(null==r.isElement?void 0:r.isElement(f)))||i?f:f.contextElement||await(null==r.getDocumentElement?void 0:r.getDocumentElement(a.floating)),boundary:c,rootBoundary:d,strategy:l})),g="floating"===h?{x:o,y:s,width:n.floating.width,height:n.floating.height}:n.reference,v=await(null==r.getOffsetParent?void 0:r.getOffsetParent(a.floating)),y=await(null==r.isElement?void 0:r.isElement(v))&&await(null==r.getScale?void 0:r.getScale(v))||{x:1,y:1},w=So(r.convertOffsetParentRelativeRectToViewportRelativeRect?await r.convertOffsetParentRelativeRectToViewportRelativeRect({elements:a,rect:g,offsetParent:v,strategy:l}):g);return{top:(m.top-w.top+b.top)/y.y,bottom:(w.bottom-m.bottom+b.bottom)/y.y,left:(m.left-w.left+b.left)/y.x,right:(w.right-m.right+b.right)/y.x}}const Po=new Set(["left","top"]);function Io(){return"undefined"!=typeof window}function Lo(t){return Ro(t)?(t.nodeName||"").toLowerCase():"#document"}function Oo(t){var e;return(null==t||null==(e=t.ownerDocument)?void 0:e.defaultView)||window}function Fo(t){var e;return null==(e=(Ro(t)?t.ownerDocument:t.document)||window.document)?void 0:e.documentElement}function Ro(t){return!!Io()&&(t instanceof Node||t instanceof Oo(t).Node)}function Do(t){return!!Io()&&(t instanceof Element||t instanceof Oo(t).Element)}function Bo(t){return!!Io()&&(t instanceof HTMLElement||t instanceof Oo(t).HTMLElement)}function No(t){return!(!Io()||"undefined"==typeof ShadowRoot)&&(t instanceof ShadowRoot||t instanceof Oo(t).ShadowRoot)}const Ho=new Set(["inline","contents"]);function Uo(t){const{overflow:e,overflowX:i,overflowY:o,display:s}=Qo(t);return/auto|scroll|overlay|hidden|clip/.test(e+o+i)&&!Ho.has(s)}const Mo=new Set(["table","td","th"]);function Vo(t){return Mo.has(Lo(t))}const jo=[":popover-open",":modal"];function Wo(t){return jo.some(e=>{try{return t.matches(e)}catch(t){return!1}})}const qo=["transform","translate","scale","rotate","perspective"],Ko=["transform","translate","scale","rotate","perspective","filter"],Go=["paint","layout","strict","content"];function Zo(t){const e=Yo(),i=Do(t)?Qo(t):t;return qo.some(t=>!!i[t]&&"none"!==i[t])||!!i.containerType&&"normal"!==i.containerType||!e&&!!i.backdropFilter&&"none"!==i.backdropFilter||!e&&!!i.filter&&"none"!==i.filter||Ko.some(t=>(i.willChange||"").includes(t))||Go.some(t=>(i.contain||"").includes(t))}function Yo(){return!("undefined"==typeof CSS||!CSS.supports)&&CSS.supports("-webkit-backdrop-filter","none")}const Xo=new Set(["html","body","#document"]);function Jo(t){return Xo.has(Lo(t))}function Qo(t){return Oo(t).getComputedStyle(t)}function ts(t){return Do(t)?{scrollLeft:t.scrollLeft,scrollTop:t.scrollTop}:{scrollLeft:t.scrollX,scrollTop:t.scrollY}}function es(t){if("html"===Lo(t))return t;const e=t.assignedSlot||t.parentNode||No(t)&&t.host||Fo(t);return No(e)?e.host:e}function is(t){const e=es(t);return Jo(e)?t.ownerDocument?t.ownerDocument.body:t.body:Bo(e)&&Uo(e)?e:is(e)}function os(t,e,i){var o;void 0===e&&(e=[]),void 0===i&&(i=!0);const s=is(t),r=s===(null==(o=t.ownerDocument)?void 0:o.body),n=Oo(s);if(r){const t=ss(n);return e.concat(n,n.visualViewport||[],Uo(s)?s:[],t&&i?os(t):[])}return e.concat(s,os(s,[],i))}function ss(t){return t.parent&&Object.getPrototypeOf(t.parent)?t.frameElement:null}function rs(t){const e=Qo(t);let i=parseFloat(e.width)||0,o=parseFloat(e.height)||0;const s=Bo(t),r=s?t.offsetWidth:i,n=s?t.offsetHeight:o,a=no(i)!==r||no(o)!==n;return a&&(i=r,o=n),{width:i,height:o,$:a}}function ns(t){return Do(t)?t:t.contextElement}function as(t){const e=ns(t);if(!Bo(e))return lo(1);const i=e.getBoundingClientRect(),{width:o,height:s,$:r}=rs(e);let n=(r?no(i.width):i.width)/o,a=(r?no(i.height):i.height)/s;return n&&Number.isFinite(n)||(n=1),a&&Number.isFinite(a)||(a=1),{x:n,y:a}}const ls=lo(0);function cs(t){const e=Oo(t);return Yo()&&e.visualViewport?{x:e.visualViewport.offsetLeft,y:e.visualViewport.offsetTop}:ls}function ds(t,e,i,o){void 0===e&&(e=!1),void 0===i&&(i=!1);const s=t.getBoundingClientRect(),r=ns(t);let n=lo(1);e&&(o?Do(o)&&(n=as(o)):n=as(t));const a=function(t,e,i){return void 0===e&&(e=!1),!(!i||e&&i!==Oo(t))&&e}(r,i,o)?cs(r):lo(0);let l=(s.left+a.x)/n.x,c=(s.top+a.y)/n.y,d=s.width/n.x,h=s.height/n.y;if(r){const t=Oo(r),e=o&&Do(o)?Oo(o):o;let i=t,s=ss(i);for(;s&&o&&e!==i;){const t=as(s),e=s.getBoundingClientRect(),o=Qo(s),r=e.left+(s.clientLeft+parseFloat(o.paddingLeft))*t.x,n=e.top+(s.clientTop+parseFloat(o.paddingTop))*t.y;l*=t.x,c*=t.y,d*=t.x,h*=t.y,l+=r,c+=n,i=Oo(s),s=ss(i)}}return So({width:d,height:h,x:l,y:c})}function hs(t,e){const i=ts(t).scrollLeft;return e?e.left+i:ds(Fo(t)).left+i}function us(t,e){const i=t.getBoundingClientRect();return{x:i.left+e.scrollLeft-hs(t,i),y:i.top+e.scrollTop}}const ps=new Set(["absolute","fixed"]);function bs(t,e,i){let o;if("viewport"===e)o=function(t,e){const i=Oo(t),o=Fo(t),s=i.visualViewport;let r=o.clientWidth,n=o.clientHeight,a=0,l=0;if(s){r=s.width,n=s.height;const t=Yo();(!t||t&&"fixed"===e)&&(a=s.offsetLeft,l=s.offsetTop)}const c=hs(o);if(c<=0){const t=o.ownerDocument,e=t.body,i=getComputedStyle(e),s="CSS1Compat"===t.compatMode&&parseFloat(i.marginLeft)+parseFloat(i.marginRight)||0,n=Math.abs(o.clientWidth-e.clientWidth-s);n<=25&&(r-=n)}else c<=25&&(r+=c);return{width:r,height:n,x:a,y:l}}(t,i);else if("document"===e)o=function(t){const e=Fo(t),i=ts(t),o=t.ownerDocument.body,s=ro(e.scrollWidth,e.clientWidth,o.scrollWidth,o.clientWidth),r=ro(e.scrollHeight,e.clientHeight,o.scrollHeight,o.clientHeight);let n=-i.scrollLeft+hs(t);const a=-i.scrollTop;return"rtl"===Qo(o).direction&&(n+=ro(e.clientWidth,o.clientWidth)-s),{width:s,height:r,x:n,y:a}}(Fo(t));else if(Do(e))o=function(t,e){const i=ds(t,!0,"fixed"===e),o=i.top+t.clientTop,s=i.left+t.clientLeft,r=Bo(t)?as(t):lo(1);return{width:t.clientWidth*r.x,height:t.clientHeight*r.y,x:s*r.x,y:o*r.y}}(e,i);else{const i=cs(t);o={x:e.x-i.x,y:e.y-i.y,width:e.width,height:e.height}}return So(o)}function fs(t,e){const i=es(t);return!(i===e||!Do(i)||Jo(i))&&("fixed"===Qo(i).position||fs(i,e))}function ms(t,e,i){const o=Bo(e),s=Fo(e),r="fixed"===i,n=ds(t,!0,r,e);let a={scrollLeft:0,scrollTop:0};const l=lo(0);function c(){l.x=hs(s)}if(o||!o&&!r)if(("body"!==Lo(e)||Uo(s))&&(a=ts(e)),o){const t=ds(e,!0,r,e);l.x=t.x+e.clientLeft,l.y=t.y+e.clientTop}else s&&c();r&&!o&&s&&c();const d=!s||o||r?lo(0):us(s,a);return{x:n.left+a.scrollLeft-l.x-d.x,y:n.top+a.scrollTop-l.y-d.y,width:n.width,height:n.height}}function gs(t){return"static"===Qo(t).position}function vs(t,e){if(!Bo(t)||"fixed"===Qo(t).position)return null;if(e)return e(t);let i=t.offsetParent;return Fo(t)===i&&(i=i.ownerDocument.body),i}function ys(t,e){const i=Oo(t);if(Wo(t))return i;if(!Bo(t)){let e=es(t);for(;e&&!Jo(e);){if(Do(e)&&!gs(e))return e;e=es(e)}return i}let o=vs(t,e);for(;o&&Vo(o)&&gs(o);)o=vs(o,e);return o&&Jo(o)&&gs(o)&&!Zo(o)?i:o||function(t){let e=es(t);for(;Bo(e)&&!Jo(e);){if(Zo(e))return e;if(Wo(e))return null;e=es(e)}return null}(t)||i}const ws={convertOffsetParentRelativeRectToViewportRelativeRect:function(t){let{elements:e,rect:i,offsetParent:o,strategy:s}=t;const r="fixed"===s,n=Fo(o),a=!!e&&Wo(e.floating);if(o===n||a&&r)return i;let l={scrollLeft:0,scrollTop:0},c=lo(1);const d=lo(0),h=Bo(o);if((h||!h&&!r)&&(("body"!==Lo(o)||Uo(n))&&(l=ts(o)),Bo(o))){const t=ds(o);c=as(o),d.x=t.x+o.clientLeft,d.y=t.y+o.clientTop}const u=!n||h||r?lo(0):us(n,l);return{width:i.width*c.x,height:i.height*c.y,x:i.x*c.x-l.scrollLeft*c.x+d.x+u.x,y:i.y*c.y-l.scrollTop*c.y+d.y+u.y}},getDocumentElement:Fo,getClippingRect:function(t){let{element:e,boundary:i,rootBoundary:o,strategy:s}=t;const r=[..."clippingAncestors"===i?Wo(e)?[]:function(t,e){const i=e.get(t);if(i)return i;let o=os(t,[],!1).filter(t=>Do(t)&&"body"!==Lo(t)),s=null;const r="fixed"===Qo(t).position;let n=r?es(t):t;for(;Do(n)&&!Jo(n);){const e=Qo(n),i=Zo(n);i||"fixed"!==e.position||(s=null),(r?!i&&!s:!i&&"static"===e.position&&s&&ps.has(s.position)||Uo(n)&&!i&&fs(t,n))?o=o.filter(t=>t!==n):s=e,n=es(n)}return e.set(t,o),o}(e,this._c):[].concat(i),o],n=r[0],a=r.reduce((t,i)=>{const o=bs(e,i,s);return t.top=ro(o.top,t.top),t.right=so(o.right,t.right),t.bottom=so(o.bottom,t.bottom),t.left=ro(o.left,t.left),t},bs(e,n,s));return{width:a.right-a.left,height:a.bottom-a.top,x:a.left,y:a.top}},getOffsetParent:ys,getElementRects:async function(t){const e=this.getOffsetParent||ys,i=this.getDimensions,o=await i(t.floating);return{reference:ms(t.reference,await e(t.floating),t.strategy),floating:{x:0,y:0,width:o.width,height:o.height}}},getClientRects:function(t){return Array.from(t.getClientRects())},getDimensions:function(t){const{width:e,height:i}=rs(t);return{width:e,height:i}},getScale:as,isElement:Do,isRTL:function(t){return"rtl"===Qo(t).direction}};function _s(t,e){return t.x===e.x&&t.y===e.y&&t.width===e.width&&t.height===e.height}const xs=function(t){return void 0===t&&(t={}),{name:"flip",options:t,async fn(e){var i,o;const{placement:s,middlewareData:r,rects:n,initialPlacement:a,platform:l,elements:c}=e,{mainAxis:d=!0,crossAxis:h=!0,fallbackPlacements:u,fallbackStrategy:p="bestFit",fallbackAxisSideDirection:b="none",flipAlignment:f=!0,...m}=po(t,e);if(null!=(i=r.arrow)&&i.alignmentOffset)return{};const g=bo(s),v=yo(a),y=bo(a)===a,w=await(null==l.isRTL?void 0:l.isRTL(c.floating)),_=u||(y||!f?[Co(a)]:function(t){const e=Co(t);return[_o(t),e,_o(e)]}(a)),x="none"!==b;!u&&x&&_.push(...function(t,e,i,o){const s=fo(t);let r=function(t,e,i){switch(t){case"top":case"bottom":return i?e?$o:xo:e?xo:$o;case"left":case"right":return e?ko:Ao;default:return[]}}(bo(t),"start"===i,o);return s&&(r=r.map(t=>t+"-"+s),e&&(r=r.concat(r.map(_o)))),r}(a,f,b,w));const $=[a,..._],k=await zo(e,m),A=[];let C=(null==(o=r.flip)?void 0:o.overflows)||[];if(d&&A.push(k[g]),h){const t=function(t,e,i){void 0===i&&(i=!1);const o=fo(t),s=wo(t),r=go(s);let n="x"===s?o===(i?"end":"start")?"right":"left":"start"===o?"bottom":"top";return e.reference[r]>e.floating[r]&&(n=Co(n)),[n,Co(n)]}(s,n,w);A.push(k[t[0]],k[t[1]])}if(C=[...C,{placement:s,overflows:A}],!A.every(t=>t<=0)){var E,S;const t=((null==(E=r.flip)?void 0:E.index)||0)+1,e=$[t];if(e&&("alignment"!==h||v===yo(e)||C.every(t=>yo(t.placement)!==v||t.overflows[0]>0)))return{data:{index:t,overflows:C},reset:{placement:e}};let i=null==(S=C.filter(t=>t.overflows[0]<=0).sort((t,e)=>t.overflows[1]-e.overflows[1])[0])?void 0:S.placement;if(!i)switch(p){case"bestFit":{var T;const t=null==(T=C.filter(t=>{if(x){const e=yo(t.placement);return e===v||"y"===e}return!0}).map(t=>[t.placement,t.overflows.filter(t=>t>0).reduce((t,e)=>t+e,0)]).sort((t,e)=>t[1]-e[1])[0])?void 0:T[0];t&&(i=t);break}case"initialPlacement":i=a}if(s!==i)return{reset:{placement:i}}}return{}}}},$s=function(t){return void 0===t&&(t={}),{name:"size",options:t,async fn(e){var i,o;const{placement:s,rects:r,platform:n,elements:a}=e,{apply:l=()=>{},...c}=po(t,e),d=await zo(e,c),h=bo(s),u=fo(s),p="y"===yo(s),{width:b,height:f}=r.floating;let m,g;"top"===h||"bottom"===h?(m=h,g=u===(await(null==n.isRTL?void 0:n.isRTL(a.floating))?"start":"end")?"left":"right"):(g=h,m="end"===u?"top":"bottom");const v=f-d.top-d.bottom,y=b-d.left-d.right,w=so(f-d[m],v),_=so(b-d[g],y),x=!e.middlewareData.shift;let $=w,k=_;if(null!=(i=e.middlewareData.shift)&&i.enabled.x&&(k=y),null!=(o=e.middlewareData.shift)&&o.enabled.y&&($=v),x&&!u){const t=ro(d.left,0),e=ro(d.right,0),i=ro(d.top,0),o=ro(d.bottom,0);p?k=b-2*(0!==t||0!==e?t+e:ro(d.left,d.right)):$=f-2*(0!==i||0!==o?i+o:ro(d.top,d.bottom))}await l({...e,availableWidth:k,availableHeight:$});const A=await n.getDimensions(a.floating);return b!==A.width||f!==A.height?{reset:{rects:!0}}:{}}}};function ks(t){return function(t){for(let e=t;e;e=As(e))if(e instanceof Element&&"none"===getComputedStyle(e).display)return null;for(let e=As(t);e;e=As(e)){if(!(e instanceof Element))continue;const t=getComputedStyle(e);if("contents"!==t.display){if("static"!==t.position||Zo(t))return e;if("BODY"===e.tagName)return e}}return null}(t)}function As(t){return t.assignedSlot?t.assignedSlot:t.parentNode instanceof ShadowRoot?t.parentNode.host:t.parentNode}var Cs=class extends We{constructor(){super(...arguments),this.localize=new to(this),this.active=!1,this.placement="top",this.strategy="absolute",this.distance=0,this.skidding=0,this.arrow=!1,this.arrowPlacement="anchor",this.arrowPadding=10,this.flip=!1,this.flipFallbackPlacements="",this.flipFallbackStrategy="best-fit",this.flipPadding=0,this.shift=!1,this.shiftPadding=0,this.autoSizePadding=0,this.hoverBridge=!1,this.updateHoverBridge=()=>{if(this.hoverBridge&&this.anchorEl){const t=this.anchorEl.getBoundingClientRect(),e=this.popup.getBoundingClientRect();let i=0,o=0,s=0,r=0,n=0,a=0,l=0,c=0;this.placement.includes("top")||this.placement.includes("bottom")?t.top<e.top?(i=t.left,o=t.bottom,s=t.right,r=t.bottom,n=e.left,a=e.top,l=e.right,c=e.top):(i=e.left,o=e.bottom,s=e.right,r=e.bottom,n=t.left,a=t.top,l=t.right,c=t.top):t.left<e.left?(i=t.right,o=t.top,s=e.left,r=e.top,n=t.right,a=t.bottom,l=e.left,c=e.bottom):(i=e.right,o=e.top,s=t.left,r=t.top,n=e.right,a=e.bottom,l=t.left,c=t.bottom),this.style.setProperty("--hover-bridge-top-left-x",`${i}px`),this.style.setProperty("--hover-bridge-top-left-y",`${o}px`),this.style.setProperty("--hover-bridge-top-right-x",`${s}px`),this.style.setProperty("--hover-bridge-top-right-y",`${r}px`),this.style.setProperty("--hover-bridge-bottom-left-x",`${n}px`),this.style.setProperty("--hover-bridge-bottom-left-y",`${a}px`),this.style.setProperty("--hover-bridge-bottom-right-x",`${l}px`),this.style.setProperty("--hover-bridge-bottom-right-y",`${c}px`)}}}async connectedCallback(){super.connectedCallback(),await this.updateComplete,this.start()}disconnectedCallback(){super.disconnectedCallback(),this.stop()}async updated(t){super.updated(t),t.has("active")&&(this.active?this.start():this.stop()),t.has("anchor")&&this.handleAnchorChange(),this.active&&(await this.updateComplete,this.reposition())}async handleAnchorChange(){if(await this.stop(),this.anchor&&"string"==typeof this.anchor){const t=this.getRootNode();this.anchorEl=t.getElementById(this.anchor)}else this.anchor instanceof Element||function(t){return null!==t&&"object"==typeof t&&"getBoundingClientRect"in t&&(!("contextElement"in t)||t.contextElement instanceof Element)}(this.anchor)?this.anchorEl=this.anchor:this.anchorEl=this.querySelector('[slot="anchor"]');this.anchorEl instanceof HTMLSlotElement&&(this.anchorEl=this.anchorEl.assignedElements({flatten:!0})[0]),this.anchorEl&&this.active&&this.start()}start(){this.anchorEl&&this.active&&(this.cleanup=function(t,e,i,o){void 0===o&&(o={});const{ancestorScroll:s=!0,ancestorResize:r=!0,elementResize:n="function"==typeof ResizeObserver,layoutShift:a="function"==typeof IntersectionObserver,animationFrame:l=!1}=o,c=ns(t),d=s||r?[...c?os(c):[],...os(e)]:[];d.forEach(t=>{s&&t.addEventListener("scroll",i,{passive:!0}),r&&t.addEventListener("resize",i)});const h=c&&a?function(t,e){let i,o=null;const s=Fo(t);function r(){var t;clearTimeout(i),null==(t=o)||t.disconnect(),o=null}return function n(a,l){void 0===a&&(a=!1),void 0===l&&(l=1),r();const c=t.getBoundingClientRect(),{left:d,top:h,width:u,height:p}=c;if(a||e(),!u||!p)return;const b={rootMargin:-ao(h)+"px "+-ao(s.clientWidth-(d+u))+"px "+-ao(s.clientHeight-(h+p))+"px "+-ao(d)+"px",threshold:ro(0,so(1,l))||1};let f=!0;function m(e){const o=e[0].intersectionRatio;if(o!==l){if(!f)return n();o?n(!1,o):i=setTimeout(()=>{n(!1,1e-7)},1e3)}1!==o||_s(c,t.getBoundingClientRect())||n(),f=!1}try{o=new IntersectionObserver(m,{...b,root:s.ownerDocument})}catch(t){o=new IntersectionObserver(m,b)}o.observe(t)}(!0),r}(c,i):null;let u,p=-1,b=null;n&&(b=new ResizeObserver(t=>{let[o]=t;o&&o.target===c&&b&&(b.unobserve(e),cancelAnimationFrame(p),p=requestAnimationFrame(()=>{var t;null==(t=b)||t.observe(e)})),i()}),c&&!l&&b.observe(c),b.observe(e));let f=l?ds(t):null;return l&&function e(){const o=ds(t);f&&!_s(f,o)&&i(),f=o,u=requestAnimationFrame(e)}(),i(),()=>{var t;d.forEach(t=>{s&&t.removeEventListener("scroll",i),r&&t.removeEventListener("resize",i)}),null==h||h(),null==(t=b)||t.disconnect(),b=null,l&&cancelAnimationFrame(u)}}(this.anchorEl,this.popup,()=>{this.reposition()}))}async stop(){return new Promise(t=>{this.cleanup?(this.cleanup(),this.cleanup=void 0,this.removeAttribute("data-current-placement"),this.style.removeProperty("--auto-size-available-width"),this.style.removeProperty("--auto-size-available-height"),requestAnimationFrame(()=>t())):t()})}reposition(){if(!this.active||!this.anchorEl)return;const t=[(e={mainAxis:this.distance,crossAxis:this.skidding},void 0===e&&(e=0),{name:"offset",options:e,async fn(t){var i,o;const{x:s,y:r,placement:n,middlewareData:a}=t,l=await async function(t,e){const{placement:i,platform:o,elements:s}=t,r=await(null==o.isRTL?void 0:o.isRTL(s.floating)),n=bo(i),a=fo(i),l="y"===yo(i),c=Po.has(n)?-1:1,d=r&&l?-1:1,h=po(e,t);let{mainAxis:u,crossAxis:p,alignmentAxis:b}="number"==typeof h?{mainAxis:h,crossAxis:0,alignmentAxis:null}:{mainAxis:h.mainAxis||0,crossAxis:h.crossAxis||0,alignmentAxis:h.alignmentAxis};return a&&"number"==typeof b&&(p="end"===a?-1*b:b),l?{x:p*d,y:u*c}:{x:u*c,y:p*d}}(t,e);return n===(null==(i=a.offset)?void 0:i.placement)&&null!=(o=a.arrow)&&o.alignmentOffset?{}:{x:s+l.x,y:r+l.y,data:{...l,placement:n}}}})];var e;this.sync?t.push($s({apply:({rects:t})=>{const e="width"===this.sync||"both"===this.sync,i="height"===this.sync||"both"===this.sync;this.popup.style.width=e?`${t.reference.width}px`:"",this.popup.style.height=i?`${t.reference.height}px`:""}})):(this.popup.style.width="",this.popup.style.height=""),this.flip&&t.push(xs({boundary:this.flipBoundary,fallbackPlacements:this.flipFallbackPlacements,fallbackStrategy:"best-fit"===this.flipFallbackStrategy?"bestFit":"initialPlacement",padding:this.flipPadding})),this.shift&&t.push(function(t){return void 0===t&&(t={}),{name:"shift",options:t,async fn(e){const{x:i,y:o,placement:s}=e,{mainAxis:r=!0,crossAxis:n=!1,limiter:a={fn:t=>{let{x:e,y:i}=t;return{x:e,y:i}}},...l}=po(t,e),c={x:i,y:o},d=await zo(e,l),h=yo(bo(s)),u=mo(h);let p=c[u],b=c[h];if(r){const t="y"===u?"bottom":"right";p=uo(p+d["y"===u?"top":"left"],p,p-d[t])}if(n){const t="y"===h?"bottom":"right";b=uo(b+d["y"===h?"top":"left"],b,b-d[t])}const f=a.fn({...e,[u]:p,[h]:b});return{...f,data:{x:f.x-i,y:f.y-o,enabled:{[u]:r,[h]:n}}}}}}({boundary:this.shiftBoundary,padding:this.shiftPadding})),this.autoSize?t.push($s({boundary:this.autoSizeBoundary,padding:this.autoSizePadding,apply:({availableWidth:t,availableHeight:e})=>{"vertical"===this.autoSize||"both"===this.autoSize?this.style.setProperty("--auto-size-available-height",`${e}px`):this.style.removeProperty("--auto-size-available-height"),"horizontal"===this.autoSize||"both"===this.autoSize?this.style.setProperty("--auto-size-available-width",`${t}px`):this.style.removeProperty("--auto-size-available-width")}})):(this.style.removeProperty("--auto-size-available-width"),this.style.removeProperty("--auto-size-available-height")),this.arrow&&t.push((t=>({name:"arrow",options:t,async fn(e){const{x:i,y:o,placement:s,rects:r,platform:n,elements:a,middlewareData:l}=e,{element:c,padding:d=0}=po(t,e)||{};if(null==c)return{};const h=Eo(d),u={x:i,y:o},p=wo(s),b=go(p),f=await n.getDimensions(c),m="y"===p,g=m?"top":"left",v=m?"bottom":"right",y=m?"clientHeight":"clientWidth",w=r.reference[b]+r.reference[p]-u[p]-r.floating[b],_=u[p]-r.reference[p],x=await(null==n.getOffsetParent?void 0:n.getOffsetParent(c));let $=x?x[y]:0;$&&await(null==n.isElement?void 0:n.isElement(x))||($=a.floating[y]||r.floating[b]);const k=w/2-_/2,A=$/2-f[b]/2-1,C=so(h[g],A),E=so(h[v],A),S=C,T=$-f[b]-E,z=$/2-f[b]/2+k,P=uo(S,z,T),I=!l.arrow&&null!=fo(s)&&z!==P&&r.reference[b]/2-(z<S?C:E)-f[b]/2<0,L=I?z<S?z-S:z-T:0;return{[p]:u[p]+L,data:{[p]:P,centerOffset:z-P-L,...I&&{alignmentOffset:L}},reset:I}}}))({element:this.arrowEl,padding:this.arrowPadding}));const i="absolute"===this.strategy?t=>ws.getOffsetParent(t,ks):ws.getOffsetParent;((t,e,i)=>{const o=new Map,s={platform:ws,...i},r={...s.platform,_c:o};return(async(t,e,i)=>{const{placement:o="bottom",strategy:s="absolute",middleware:r=[],platform:n}=i,a=r.filter(Boolean),l=await(null==n.isRTL?void 0:n.isRTL(e));let c=await n.getElementRects({reference:t,floating:e,strategy:s}),{x:d,y:h}=To(c,o,l),u=o,p={},b=0;for(let i=0;i<a.length;i++){const{name:r,fn:f}=a[i],{x:m,y:g,data:v,reset:y}=await f({x:d,y:h,initialPlacement:o,placement:u,strategy:s,middlewareData:p,rects:c,platform:n,elements:{reference:t,floating:e}});d=null!=m?m:d,h=null!=g?g:h,p={...p,[r]:{...p[r],...v}},y&&b<=50&&(b++,"object"==typeof y&&(y.placement&&(u=y.placement),y.rects&&(c=!0===y.rects?await n.getElementRects({reference:t,floating:e,strategy:s}):y.rects),({x:d,y:h}=To(c,u,l))),i=-1)}return{x:d,y:h,placement:u,strategy:s,middlewareData:p}})(t,e,{...s,platform:r})})(this.anchorEl,this.popup,{placement:this.placement,middleware:t,strategy:this.strategy,platform:Ie(Pe({},ws),{getOffsetParent:i})}).then(({x:t,y:e,middlewareData:i,placement:o})=>{const s="rtl"===this.localize.dir(),r={top:"bottom",right:"left",bottom:"top",left:"right"}[o.split("-")[0]];if(this.setAttribute("data-current-placement",o),Object.assign(this.popup.style,{left:`${t}px`,top:`${e}px`}),this.arrow){const t=i.arrow.x,e=i.arrow.y;let o="",n="",a="",l="";if("start"===this.arrowPlacement){const i="number"==typeof t?`calc(${this.arrowPadding}px - var(--arrow-padding-offset))`:"";o="number"==typeof e?`calc(${this.arrowPadding}px - var(--arrow-padding-offset))`:"",n=s?i:"",l=s?"":i}else if("end"===this.arrowPlacement){const i="number"==typeof t?`calc(${this.arrowPadding}px - var(--arrow-padding-offset))`:"";n=s?"":i,l=s?i:"",a="number"==typeof e?`calc(${this.arrowPadding}px - var(--arrow-padding-offset))`:""}else"center"===this.arrowPlacement?(l="number"==typeof t?"calc(50% - var(--arrow-size-diagonal))":"",o="number"==typeof e?"calc(50% - var(--arrow-size-diagonal))":""):(l="number"==typeof t?`${t}px`:"",o="number"==typeof e?`${e}px`:"");Object.assign(this.arrowEl.style,{top:o,right:n,bottom:a,left:l,[r]:"calc(var(--arrow-size-diagonal) * -1)"})}}),requestAnimationFrame(()=>this.updateHoverBridge()),this.emit("sl-reposition")}render(){return Xt`
      <slot name="anchor" @slotchange=${this.handleAnchorChange}></slot>

      <span
        part="hover-bridge"
        class=${$i({"popup-hover-bridge":!0,"popup-hover-bridge--visible":this.hoverBridge&&this.active})}
      ></span>

      <div
        part="popup"
        class=${$i({popup:!0,"popup--active":this.active,"popup--fixed":"fixed"===this.strategy,"popup--has-arrow":this.arrow})}
      >
        <slot></slot>
        ${this.arrow?Xt`<div part="arrow" class="popup__arrow" role="presentation"></div>`:""}
      </div>
    `}};Cs.styles=[De,oo],Le([Ve(".popup")],Cs.prototype,"popup",2),Le([Ve(".popup__arrow")],Cs.prototype,"arrowEl",2),Le([He()],Cs.prototype,"anchor",2),Le([He({type:Boolean,reflect:!0})],Cs.prototype,"active",2),Le([He({reflect:!0})],Cs.prototype,"placement",2),Le([He({reflect:!0})],Cs.prototype,"strategy",2),Le([He({type:Number})],Cs.prototype,"distance",2),Le([He({type:Number})],Cs.prototype,"skidding",2),Le([He({type:Boolean})],Cs.prototype,"arrow",2),Le([He({attribute:"arrow-placement"})],Cs.prototype,"arrowPlacement",2),Le([He({attribute:"arrow-padding",type:Number})],Cs.prototype,"arrowPadding",2),Le([He({type:Boolean})],Cs.prototype,"flip",2),Le([He({attribute:"flip-fallback-placements",converter:{fromAttribute:t=>t.split(" ").map(t=>t.trim()).filter(t=>""!==t),toAttribute:t=>t.join(" ")}})],Cs.prototype,"flipFallbackPlacements",2),Le([He({attribute:"flip-fallback-strategy"})],Cs.prototype,"flipFallbackStrategy",2),Le([He({type:Object})],Cs.prototype,"flipBoundary",2),Le([He({attribute:"flip-padding",type:Number})],Cs.prototype,"flipPadding",2),Le([He({type:Boolean})],Cs.prototype,"shift",2),Le([He({type:Object})],Cs.prototype,"shiftBoundary",2),Le([He({attribute:"shift-padding",type:Number})],Cs.prototype,"shiftPadding",2),Le([He({attribute:"auto-size"})],Cs.prototype,"autoSize",2),Le([He()],Cs.prototype,"sync",2),Le([He({type:Object})],Cs.prototype,"autoSizeBoundary",2),Le([He({attribute:"auto-size-padding",type:Number})],Cs.prototype,"autoSizePadding",2),Le([He({attribute:"hover-bridge",type:Boolean})],Cs.prototype,"hoverBridge",2);var Es=class extends We{constructor(){super(),this.localize=new to(this),this.content="",this.placement="top",this.disabled=!1,this.distance=8,this.open=!1,this.skidding=0,this.trigger="hover focus",this.hoist=!1,this.handleBlur=()=>{this.hasTrigger("focus")&&this.hide()},this.handleClick=()=>{this.hasTrigger("click")&&(this.open?this.hide():this.show())},this.handleFocus=()=>{this.hasTrigger("focus")&&this.show()},this.handleDocumentKeyDown=t=>{"Escape"===t.key&&(t.stopPropagation(),this.hide())},this.handleMouseOver=()=>{if(this.hasTrigger("hover")){const t=Ni(getComputedStyle(this).getPropertyValue("--show-delay"));clearTimeout(this.hoverTimeout),this.hoverTimeout=window.setTimeout(()=>this.show(),t)}},this.handleMouseOut=()=>{if(this.hasTrigger("hover")){const t=Ni(getComputedStyle(this).getPropertyValue("--hide-delay"));clearTimeout(this.hoverTimeout),this.hoverTimeout=window.setTimeout(()=>this.hide(),t)}},this.addEventListener("blur",this.handleBlur,!0),this.addEventListener("focus",this.handleFocus,!0),this.addEventListener("click",this.handleClick),this.addEventListener("mouseover",this.handleMouseOver),this.addEventListener("mouseout",this.handleMouseOut)}disconnectedCallback(){var t;super.disconnectedCallback(),null==(t=this.closeWatcher)||t.destroy(),document.removeEventListener("keydown",this.handleDocumentKeyDown)}firstUpdated(){this.body.hidden=!this.open,this.open&&(this.popup.active=!0,this.popup.reposition())}hasTrigger(t){return this.trigger.split(" ").includes(t)}async handleOpenChange(){var t,e;if(this.open){if(this.disabled)return;this.emit("sl-show"),"CloseWatcher"in window?(null==(t=this.closeWatcher)||t.destroy(),this.closeWatcher=new CloseWatcher,this.closeWatcher.onclose=()=>{this.hide()}):document.addEventListener("keydown",this.handleDocumentKeyDown),await Hi(this.body),this.body.hidden=!1,this.popup.active=!0;const{keyframes:e,options:i}=Ri(this,"tooltip.show",{dir:this.localize.dir()});await Bi(this.popup.popup,e,i),this.popup.reposition(),this.emit("sl-after-show")}else{this.emit("sl-hide"),null==(e=this.closeWatcher)||e.destroy(),document.removeEventListener("keydown",this.handleDocumentKeyDown),await Hi(this.body);const{keyframes:t,options:i}=Ri(this,"tooltip.hide",{dir:this.localize.dir()});await Bi(this.popup.popup,t,i),this.popup.active=!1,this.body.hidden=!0,this.emit("sl-after-hide")}}async handleOptionsChange(){this.hasUpdated&&(await this.updateComplete,this.popup.reposition())}handleDisabledChange(){this.disabled&&this.open&&this.hide()}async show(){if(!this.open)return this.open=!0,Di(this,"sl-after-show")}async hide(){if(this.open)return this.open=!1,Di(this,"sl-after-hide")}render(){return Xt`
      <sl-popup
        part="base"
        exportparts="
          popup:base__popup,
          arrow:base__arrow
        "
        class=${$i({tooltip:!0,"tooltip--open":this.open})}
        placement=${this.placement}
        distance=${this.distance}
        skidding=${this.skidding}
        strategy=${this.hoist?"fixed":"absolute"}
        flip
        shift
        arrow
        hover-bridge
      >
        ${""}
        <slot slot="anchor" aria-describedby="tooltip"></slot>

        ${""}
        <div part="body" id="tooltip" class="tooltip__body" role="tooltip" aria-live=${this.open?"polite":"off"}>
          <slot name="content">${this.content}</slot>
        </div>
      </sl-popup>
    `}};Es.styles=[De,io],Es.dependencies={"sl-popup":Cs},Le([Ve("slot:not([name])")],Es.prototype,"defaultSlot",2),Le([Ve(".tooltip__body")],Es.prototype,"body",2),Le([Ve("sl-popup")],Es.prototype,"popup",2),Le([He()],Es.prototype,"content",2),Le([He()],Es.prototype,"placement",2),Le([He({type:Boolean,reflect:!0})],Es.prototype,"disabled",2),Le([He({type:Number})],Es.prototype,"distance",2),Le([He({type:Boolean,reflect:!0})],Es.prototype,"open",2),Le([He({type:Number})],Es.prototype,"skidding",2),Le([He()],Es.prototype,"trigger",2),Le([He({type:Boolean})],Es.prototype,"hoist",2),Le([Re("open",{waitUntilFirstUpdate:!0})],Es.prototype,"handleOpenChange",1),Le([Re(["content","distance","hoist","placement","skidding"])],Es.prototype,"handleOptionsChange",1),Le([Re("disabled")],Es.prototype,"handleDisabledChange",1),Fi("tooltip.show",{keyframes:[{opacity:0,scale:.8},{opacity:1,scale:1}],options:{duration:150,easing:"ease"}}),Fi("tooltip.hide",{keyframes:[{opacity:1,scale:1},{opacity:0,scale:.8}],options:{duration:150,easing:"ease"}}),Es.define("sl-tooltip");const{I:Ss}=it,Ts=t=>(...e)=>({_$litDirective$:t,values:e});class zs{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,i){this._$Ct=t,this._$AM=e,this._$Ci=i}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}}const Ps=(t,e)=>{var i,o;const s=t._$AN;if(void 0===s)return!1;for(const t of s)null===(o=(i=t)._$AO)||void 0===o||o.call(i,e,!1),Ps(t,e);return!0},Is=t=>{let e,i;do{if(void 0===(e=t._$AM))break;i=e._$AN,i.delete(t),t=e}while(0===(null==i?void 0:i.size))},Ls=t=>{for(let e;e=t._$AM;t=e){let i=e._$AN;if(void 0===i)e._$AN=i=new Set;else if(i.has(t))break;i.add(t),Rs(e)}};function Os(t){void 0!==this._$AN?(Is(this),this._$AM=t,Ls(this)):this._$AM=t}function Fs(t,e=!1,i=0){const o=this._$AH,s=this._$AN;if(void 0!==s&&0!==s.size)if(e)if(Array.isArray(o))for(let t=i;t<o.length;t++)Ps(o[t],!1),Is(o[t]);else null!=o&&(Ps(o,!1),Is(o));else Ps(this,t)}const Rs=t=>{var e,i,o,s;2==t.type&&(null!==(e=(o=t)._$AP)&&void 0!==e||(o._$AP=Fs),null!==(i=(s=t)._$AQ)&&void 0!==i||(s._$AQ=Os))};class Ds extends zs{constructor(){super(...arguments),this._$AN=void 0}_$AT(t,e,i){super._$AT(t,e,i),Ls(this),this.isConnected=t._$AU}_$AO(t,e=!0){var i,o;t!==this.isConnected&&(this.isConnected=t,t?null===(i=this.reconnected)||void 0===i||i.call(this):null===(o=this.disconnected)||void 0===o||o.call(this)),e&&(Ps(this,t),Is(this))}setValue(t){if((()=>void 0===this._$Ct.strings)())this._$Ct._$AI(t,this);else{const e=[...this._$Ct._$AH];e[this._$Ci]=t,this._$Ct._$AI(e,this,0)}}disconnected(){}reconnected(){}}class Bs{constructor(t){this.G=t}disconnect(){this.G=void 0}reconnect(t){this.G=t}deref(){return this.G}}class Ns{constructor(){this.Y=void 0,this.Z=void 0}get(){return this.Y}pause(){var t;null!==(t=this.Y)&&void 0!==t||(this.Y=new Promise(t=>this.Z=t))}resume(){var t;null===(t=this.Z)||void 0===t||t.call(this),this.Y=this.Z=void 0}}const Hs=t=>!(t=>null===t||"object"!=typeof t&&"function"!=typeof t)(t)&&"function"==typeof t.then,Us=1073741823,Ms=Ts(class extends Ds{constructor(){super(...arguments),this._$C_t=Us,this._$Cwt=[],this._$Cq=new Bs(this),this._$CK=new Ns}render(...t){var e;return null!==(e=t.find(t=>!Hs(t)))&&void 0!==e?e:H}update(t,e){const i=this._$Cwt;let o=i.length;this._$Cwt=e;const s=this._$Cq,r=this._$CK;this.isConnected||this.disconnected();for(let t=0;t<e.length&&!(t>this._$C_t);t++){const n=e[t];if(!Hs(n))return this._$C_t=t,n;t<o&&n===i[t]||(this._$C_t=Us,o=0,Promise.resolve(n).then(async t=>{for(;r.get();)await r.get();const e=s.deref();if(void 0!==e){const i=e._$Cwt.indexOf(n);i>-1&&i<e._$C_t&&(e._$C_t=i,e.setValue(t))}}))}return H}disconnected(){this._$Cq.disconnect(),this._$CK.pause()}reconnected(){this._$Cq.reconnect(this),this._$CK.resume()}});class Vs{constructor(t){this.message=t,this.name="InvalidTableFileException"}}class js extends nt{static properties={file:{type:File},template:{attribute:!1}};static styles=r`
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
    `;getWidth(t){return Math.min(100,20*(t-2))}async*makeTextFileLineIterator(t){const e=new TextDecoder("utf-8"),i=t.stream().getReader();let{value:o,done:s}=await i.read();o=o?e.decode(o,{stream:!0}):"";const r=/\r\n|\n|\r/gm;let n=0;for(;;){const t=r.exec(o);if(!t){if(s)break;const t=o.substr(n);({value:o,done:s}=await i.read()),o=t+(o?e.decode(o,{stream:!0}):""),n=r.lastIndex=0;continue}yield o.substring(n,t.index),n=r.lastIndex}n<o.length&&(yield o.substr(n))}render(){if(!this.file)return N``;const t=this.parseSrc();return N`${Ms(t,N``)}`}}customElements.define("sc-report-table",js),customElements.define("sc-intro-tbl",class extends js{parseHeader(t){const e=t.split(";");return N`
            <tr>
                ${e.map(t=>N`<th>${t}</th>`)}
            </tr>
        `}parseRow(t){let e=N``,i=!0;for(const o of t.split(";")){const[t,s,r]=o.split("|");let n=N`${t}`;r&&(n=N`<a href=${r}>${n}</a>`),s&&(n=N`<abbr title=${s}>${n}</abbr>`),i?(e=N`${e}
                    <td class="td-colname">
                        ${n}
                    </td>
                `,i=!1):e=N`${e}
                    <td>
                        ${n}
                    </td>
                `}return N`<tr>${e}</tr>`}async parseSrc(){const t=this.makeTextFileLineIterator(this.file);let e=await t.next();if(e=e.value,!e.startsWith("H;"))throw new Vs("first line in intro table file should be a header.");e=e.slice(2);let i=this.parseHeader(e);for await(let e of t){if(!e.startsWith("R;"))throw new Vs("lines following the first should all be normal table rows.");e=e.slice(2),i=N`${i}${this.parseRow(e)}`}return N`<table>${i}</table>`}});var Ws=pt`
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
    overflow: hidden;
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

  .alert--has-countdown {
    border-bottom: none;
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
    margin-inline-end: var(--sl-spacing-medium);
    align-self: center;
  }

  .alert__countdown {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: calc(var(--sl-panel-border-width) * 3);
    background-color: var(--sl-panel-border-color);
    display: flex;
  }

  .alert__countdown--ltr {
    justify-content: flex-end;
  }

  .alert__countdown .alert__countdown-elapsed {
    height: 100%;
    width: 0;
  }

  .alert--primary .alert__countdown-elapsed {
    background-color: var(--sl-color-primary-600);
  }

  .alert--success .alert__countdown-elapsed {
    background-color: var(--sl-color-success-600);
  }

  .alert--neutral .alert__countdown-elapsed {
    background-color: var(--sl-color-neutral-600);
  }

  .alert--warning .alert__countdown-elapsed {
    background-color: var(--sl-color-warning-600);
  }

  .alert--danger .alert__countdown-elapsed {
    background-color: var(--sl-color-danger-600);
  }

  .alert__timer {
    display: none;
  }
`,qs=class t extends We{constructor(){super(...arguments),this.hasSlotController=new Mi(this,"icon","suffix"),this.localize=new to(this),this.open=!1,this.closable=!1,this.variant="primary",this.duration=1/0,this.remainingTime=this.duration}static get toastStack(){return this.currentToastStack||(this.currentToastStack=Object.assign(document.createElement("div"),{className:"sl-toast-stack"})),this.currentToastStack}firstUpdated(){this.base.hidden=!this.open}restartAutoHide(){this.handleCountdownChange(),clearTimeout(this.autoHideTimeout),clearInterval(this.remainingTimeInterval),this.open&&this.duration<1/0&&(this.autoHideTimeout=window.setTimeout(()=>this.hide(),this.duration),this.remainingTime=this.duration,this.remainingTimeInterval=window.setInterval(()=>{this.remainingTime-=100},100))}pauseAutoHide(){var t;null==(t=this.countdownAnimation)||t.pause(),clearTimeout(this.autoHideTimeout),clearInterval(this.remainingTimeInterval)}resumeAutoHide(){var t;this.duration<1/0&&(this.autoHideTimeout=window.setTimeout(()=>this.hide(),this.remainingTime),this.remainingTimeInterval=window.setInterval(()=>{this.remainingTime-=100},100),null==(t=this.countdownAnimation)||t.play())}handleCountdownChange(){if(this.open&&this.duration<1/0&&this.countdown){const{countdownElement:t}=this,e="100%",i="0";this.countdownAnimation=t.animate([{width:e},{width:i}],{duration:this.duration,easing:"linear"})}}handleCloseClick(){this.hide()}async handleOpenChange(){if(this.open){this.emit("sl-show"),this.duration<1/0&&this.restartAutoHide(),await Hi(this.base),this.base.hidden=!1;const{keyframes:t,options:e}=Ri(this,"alert.show",{dir:this.localize.dir()});await Bi(this.base,t,e),this.emit("sl-after-show")}else{si(this),this.emit("sl-hide"),clearTimeout(this.autoHideTimeout),clearInterval(this.remainingTimeInterval),await Hi(this.base);const{keyframes:t,options:e}=Ri(this,"alert.hide",{dir:this.localize.dir()});await Bi(this.base,t,e),this.base.hidden=!0,this.emit("sl-after-hide")}}handleDurationChange(){this.restartAutoHide()}async show(){if(!this.open)return this.open=!0,Di(this,"sl-after-show")}async hide(){if(this.open)return this.open=!1,Di(this,"sl-after-hide")}async toast(){return new Promise(e=>{this.handleCountdownChange(),null===t.toastStack.parentElement&&document.body.append(t.toastStack),t.toastStack.appendChild(this),requestAnimationFrame(()=>{this.clientWidth,this.show()}),this.addEventListener("sl-after-hide",()=>{t.toastStack.removeChild(this),e(),null===t.toastStack.querySelector("sl-alert")&&t.toastStack.remove()},{once:!0})})}render(){return Xt`
      <div
        part="base"
        class=${$i({alert:!0,"alert--open":this.open,"alert--closable":this.closable,"alert--has-countdown":!!this.countdown,"alert--has-icon":this.hasSlotController.test("icon"),"alert--primary":"primary"===this.variant,"alert--success":"success"===this.variant,"alert--neutral":"neutral"===this.variant,"alert--warning":"warning"===this.variant,"alert--danger":"danger"===this.variant})}
        role="alert"
        aria-hidden=${this.open?"false":"true"}
        @mouseenter=${this.pauseAutoHide}
        @mouseleave=${this.resumeAutoHide}
      >
        <div part="icon" class="alert__icon">
          <slot name="icon"></slot>
        </div>

        <div part="message" class="alert__message" aria-live="polite">
          <slot></slot>
        </div>

        ${this.closable?Xt`
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

        <div role="timer" class="alert__timer">${this.remainingTime}</div>

        ${this.countdown?Xt`
              <div
                class=${$i({alert__countdown:!0,"alert__countdown--ltr":"ltr"===this.countdown})}
              >
                <div class="alert__countdown-elapsed"></div>
              </div>
            `:""}
      </div>
    `}};qs.styles=[De,Ws],qs.dependencies={"sl-icon-button":Pi},Le([Ve('[part~="base"]')],qs.prototype,"base",2),Le([Ve(".alert__countdown-elapsed")],qs.prototype,"countdownElement",2),Le([He({type:Boolean,reflect:!0})],qs.prototype,"open",2),Le([He({type:Boolean,reflect:!0})],qs.prototype,"closable",2),Le([He({reflect:!0})],qs.prototype,"variant",2),Le([He({type:Number})],qs.prototype,"duration",2),Le([He({type:String,reflect:!0})],qs.prototype,"countdown",2),Le([Ue()],qs.prototype,"remainingTime",2),Le([Re("open",{waitUntilFirstUpdate:!0})],qs.prototype,"handleOpenChange",1),Le([Re("duration")],qs.prototype,"handleDurationChange",1);var Ks=qs;Fi("alert.show",{keyframes:[{opacity:0,scale:.8},{opacity:1,scale:1}],options:{duration:250,easing:"ease"}}),Fi("alert.hide",{keyframes:[{opacity:1,scale:1},{opacity:0,scale:.8}],options:{duration:250,easing:"ease"}}),Ks.define("sl-alert");var Gs=pt`
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
    transition:
      var(--sl-transition-fast) translate ease,
      var(--sl-transition-fast) width ease;
  }

  .tab-group--has-scroll-controls .tab-group__nav-container {
    position: relative;
    padding: 0 var(--sl-spacing-x-large);
  }

  .tab-group--has-scroll-controls .tab-group__scroll-button--start--hidden,
  .tab-group--has-scroll-controls .tab-group__scroll-button--end--hidden {
    visibility: hidden;
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
`,Zs=pt`
  :host {
    display: contents;
  }
`,Ys=class extends We{constructor(){super(...arguments),this.observedElements=[],this.disabled=!1}connectedCallback(){super.connectedCallback(),this.resizeObserver=new ResizeObserver(t=>{this.emit("sl-resize",{detail:{entries:t}})}),this.disabled||this.startObserver()}disconnectedCallback(){super.disconnectedCallback(),this.stopObserver()}handleSlotChange(){this.disabled||this.startObserver()}startObserver(){const t=this.shadowRoot.querySelector("slot");if(null!==t){const e=t.assignedElements({flatten:!0});this.observedElements.forEach(t=>this.resizeObserver.unobserve(t)),this.observedElements=[],e.forEach(t=>{this.resizeObserver.observe(t),this.observedElements.push(t)})}}stopObserver(){this.resizeObserver.disconnect()}handleDisabledChange(){this.disabled?this.stopObserver():this.startObserver()}render(){return Xt` <slot @slotchange=${this.handleSlotChange}></slot> `}};Ys.styles=[De,Zs],Le([He({type:Boolean,reflect:!0})],Ys.prototype,"disabled",2),Le([Re("disabled",{waitUntilFirstUpdate:!0})],Ys.prototype,"handleDisabledChange",1);var Xs,Js=class extends We{constructor(){super(...arguments),this.tabs=[],this.focusableTabs=[],this.panels=[],this.localize=new to(this),this.hasScrollControls=!1,this.shouldHideScrollStartButton=!1,this.shouldHideScrollEndButton=!1,this.placement="top",this.activation="auto",this.noScrollControls=!1,this.fixedScrollControls=!1,this.scrollOffset=1}connectedCallback(){const t=Promise.all([customElements.whenDefined("sl-tab"),customElements.whenDefined("sl-tab-panel")]);super.connectedCallback(),this.resizeObserver=new ResizeObserver(()=>{this.repositionIndicator(),this.updateScrollControls()}),this.mutationObserver=new MutationObserver(t=>{const e=t.filter(({target:t})=>{if(t===this)return!0;if(t.closest("sl-tab-group")!==this)return!1;const e=t.tagName.toLowerCase();return"sl-tab"===e||"sl-tab-panel"===e});if(0!==e.length)if(e.some(t=>!["aria-labelledby","aria-controls"].includes(t.attributeName))&&setTimeout(()=>this.setAriaLabels()),e.some(t=>"disabled"===t.attributeName))this.syncTabsAndPanels();else if(e.some(t=>"active"===t.attributeName)){const t=e.filter(t=>"active"===t.attributeName&&"sl-tab"===t.target.tagName.toLowerCase()).map(t=>t.target),i=t.find(t=>t.active);i&&this.setActiveTab(i)}}),this.updateComplete.then(()=>{this.syncTabsAndPanels(),this.mutationObserver.observe(this,{attributes:!0,attributeFilter:["active","disabled","name","panel"],childList:!0,subtree:!0}),this.resizeObserver.observe(this.nav),t.then(()=>{new IntersectionObserver((t,e)=>{var i;t[0].intersectionRatio>0&&(this.setAriaLabels(),this.setActiveTab(null!=(i=this.getActiveTab())?i:this.tabs[0],{emitEvents:!1}),e.unobserve(t[0].target))}).observe(this.tabGroup)})})}disconnectedCallback(){var t,e;super.disconnectedCallback(),null==(t=this.mutationObserver)||t.disconnect(),this.nav&&(null==(e=this.resizeObserver)||e.unobserve(this.nav))}getAllTabs(){return this.shadowRoot.querySelector('slot[name="nav"]').assignedElements()}getAllPanels(){return[...this.body.assignedElements()].filter(t=>"sl-tab-panel"===t.tagName.toLowerCase())}getActiveTab(){return this.tabs.find(t=>t.active)}handleClick(t){const e=t.target.closest("sl-tab");(null==e?void 0:e.closest("sl-tab-group"))===this&&null!==e&&this.setActiveTab(e,{scrollBehavior:"smooth"})}handleKeyDown(t){const e=t.target.closest("sl-tab");if((null==e?void 0:e.closest("sl-tab-group"))===this&&(["Enter"," "].includes(t.key)&&null!==e&&(this.setActiveTab(e,{scrollBehavior:"smooth"}),t.preventDefault()),["ArrowLeft","ArrowRight","ArrowUp","ArrowDown","Home","End"].includes(t.key))){const e=this.tabs.find(t=>t.matches(":focus")),i="rtl"===this.localize.dir();let o=null;if("sl-tab"===(null==e?void 0:e.tagName.toLowerCase())){if("Home"===t.key)o=this.focusableTabs[0];else if("End"===t.key)o=this.focusableTabs[this.focusableTabs.length-1];else if(["top","bottom"].includes(this.placement)&&t.key===(i?"ArrowRight":"ArrowLeft")||["start","end"].includes(this.placement)&&"ArrowUp"===t.key){const t=this.tabs.findIndex(t=>t===e);o=this.findNextFocusableTab(t,"backward")}else if(["top","bottom"].includes(this.placement)&&t.key===(i?"ArrowLeft":"ArrowRight")||["start","end"].includes(this.placement)&&"ArrowDown"===t.key){const t=this.tabs.findIndex(t=>t===e);o=this.findNextFocusableTab(t,"forward")}if(!o)return;o.tabIndex=0,o.focus({preventScroll:!0}),"auto"===this.activation?this.setActiveTab(o,{scrollBehavior:"smooth"}):this.tabs.forEach(t=>{t.tabIndex=t===o?0:-1}),["top","bottom"].includes(this.placement)&&ii(o,this.nav,"horizontal"),t.preventDefault()}}}handleScrollToStart(){this.nav.scroll({left:"rtl"===this.localize.dir()?this.nav.scrollLeft+this.nav.clientWidth:this.nav.scrollLeft-this.nav.clientWidth,behavior:"smooth"})}handleScrollToEnd(){this.nav.scroll({left:"rtl"===this.localize.dir()?this.nav.scrollLeft-this.nav.clientWidth:this.nav.scrollLeft+this.nav.clientWidth,behavior:"smooth"})}setActiveTab(t,e){if(e=Pe({emitEvents:!0,scrollBehavior:"auto"},e),t!==this.activeTab&&!t.disabled){const i=this.activeTab;this.activeTab=t,this.tabs.forEach(t=>{t.active=t===this.activeTab,t.tabIndex=t===this.activeTab?0:-1}),this.panels.forEach(t=>{var e;return t.active=t.name===(null==(e=this.activeTab)?void 0:e.panel)}),this.syncIndicator(),["top","bottom"].includes(this.placement)&&ii(this.activeTab,this.nav,"horizontal",e.scrollBehavior),e.emitEvents&&(i&&this.emit("sl-tab-hide",{detail:{name:i.panel}}),this.emit("sl-tab-show",{detail:{name:this.activeTab.panel}}))}}setAriaLabels(){this.tabs.forEach(t=>{const e=this.panels.find(e=>e.name===t.panel);e&&(t.setAttribute("aria-controls",e.getAttribute("id")),e.setAttribute("aria-labelledby",t.getAttribute("id")))})}repositionIndicator(){const t=this.getActiveTab();if(!t)return;const e=t.clientWidth,i=t.clientHeight,o="rtl"===this.localize.dir(),s=this.getAllTabs(),r=s.slice(0,s.indexOf(t)).reduce((t,e)=>({left:t.left+e.clientWidth,top:t.top+e.clientHeight}),{left:0,top:0});switch(this.placement){case"top":case"bottom":this.indicator.style.width=`${e}px`,this.indicator.style.height="auto",this.indicator.style.translate=o?-1*r.left+"px":`${r.left}px`;break;case"start":case"end":this.indicator.style.width="auto",this.indicator.style.height=`${i}px`,this.indicator.style.translate=`0 ${r.top}px`}}syncTabsAndPanels(){this.tabs=this.getAllTabs(),this.focusableTabs=this.tabs.filter(t=>!t.disabled),this.panels=this.getAllPanels(),this.syncIndicator(),this.updateComplete.then(()=>this.updateScrollControls())}findNextFocusableTab(t,e){let i=null;const o="forward"===e?1:-1;let s=t+o;for(;t<this.tabs.length;){if(i=this.tabs[s]||null,null===i){i="forward"===e?this.focusableTabs[0]:this.focusableTabs[this.focusableTabs.length-1];break}if(!i.disabled)break;s+=o}return i}updateScrollButtons(){this.hasScrollControls&&!this.fixedScrollControls&&(this.shouldHideScrollStartButton=this.scrollFromStart()<=this.scrollOffset,this.shouldHideScrollEndButton=this.isScrolledToEnd())}isScrolledToEnd(){return this.scrollFromStart()+this.nav.clientWidth>=this.nav.scrollWidth-this.scrollOffset}scrollFromStart(){return"rtl"===this.localize.dir()?-this.nav.scrollLeft:this.nav.scrollLeft}updateScrollControls(){this.noScrollControls?this.hasScrollControls=!1:this.hasScrollControls=["top","bottom"].includes(this.placement)&&this.nav.scrollWidth>this.nav.clientWidth+1,this.updateScrollButtons()}syncIndicator(){this.getActiveTab()?(this.indicator.style.display="block",this.repositionIndicator()):this.indicator.style.display="none"}show(t){const e=this.tabs.find(e=>e.panel===t);e&&this.setActiveTab(e,{scrollBehavior:"smooth"})}render(){const t="rtl"===this.localize.dir();return Xt`
      <div
        part="base"
        class=${$i({"tab-group":!0,"tab-group--top":"top"===this.placement,"tab-group--bottom":"bottom"===this.placement,"tab-group--start":"start"===this.placement,"tab-group--end":"end"===this.placement,"tab-group--rtl":"rtl"===this.localize.dir(),"tab-group--has-scroll-controls":this.hasScrollControls})}
        @click=${this.handleClick}
        @keydown=${this.handleKeyDown}
      >
        <div class="tab-group__nav-container" part="nav">
          ${this.hasScrollControls?Xt`
                <sl-icon-button
                  part="scroll-button scroll-button--start"
                  exportparts="base:scroll-button__base"
                  class=${$i({"tab-group__scroll-button":!0,"tab-group__scroll-button--start":!0,"tab-group__scroll-button--start--hidden":this.shouldHideScrollStartButton})}
                  name=${t?"chevron-right":"chevron-left"}
                  library="system"
                  tabindex="-1"
                  aria-hidden="true"
                  label=${this.localize.term("scrollToStart")}
                  @click=${this.handleScrollToStart}
                ></sl-icon-button>
              `:""}

          <div class="tab-group__nav" @scrollend=${this.updateScrollButtons}>
            <div part="tabs" class="tab-group__tabs" role="tablist">
              <div part="active-tab-indicator" class="tab-group__indicator"></div>
              <sl-resize-observer @sl-resize=${this.syncIndicator}>
                <slot name="nav" @slotchange=${this.syncTabsAndPanels}></slot>
              </sl-resize-observer>
            </div>
          </div>

          ${this.hasScrollControls?Xt`
                <sl-icon-button
                  part="scroll-button scroll-button--end"
                  exportparts="base:scroll-button__base"
                  class=${$i({"tab-group__scroll-button":!0,"tab-group__scroll-button--end":!0,"tab-group__scroll-button--end--hidden":this.shouldHideScrollEndButton})}
                  name=${t?"chevron-left":"chevron-right"}
                  library="system"
                  tabindex="-1"
                  aria-hidden="true"
                  label=${this.localize.term("scrollToEnd")}
                  @click=${this.handleScrollToEnd}
                ></sl-icon-button>
              `:""}
        </div>

        <slot part="body" class="tab-group__body" @slotchange=${this.syncTabsAndPanels}></slot>
      </div>
    `}};Js.styles=[De,Gs],Js.dependencies={"sl-icon-button":Pi,"sl-resize-observer":Ys},Le([Ve(".tab-group")],Js.prototype,"tabGroup",2),Le([Ve(".tab-group__body")],Js.prototype,"body",2),Le([Ve(".tab-group__nav")],Js.prototype,"nav",2),Le([Ve(".tab-group__indicator")],Js.prototype,"indicator",2),Le([Ue()],Js.prototype,"hasScrollControls",2),Le([Ue()],Js.prototype,"shouldHideScrollStartButton",2),Le([Ue()],Js.prototype,"shouldHideScrollEndButton",2),Le([He()],Js.prototype,"placement",2),Le([He()],Js.prototype,"activation",2),Le([He({attribute:"no-scroll-controls",type:Boolean})],Js.prototype,"noScrollControls",2),Le([He({attribute:"fixed-scroll-controls",type:Boolean})],Js.prototype,"fixedScrollControls",2),Le([(Xs={passive:!0},(t,e)=>{const i="function"==typeof t?t:t[e];Object.assign(i,Xs)})],Js.prototype,"updateScrollButtons",1),Le([Re("noScrollControls",{waitUntilFirstUpdate:!0})],Js.prototype,"updateScrollControls",1),Le([Re("placement",{waitUntilFirstUpdate:!0})],Js.prototype,"syncIndicator",1),Js.define("sl-tab-group");var Qs=(t,e)=>{let i=0;return function(...o){window.clearTimeout(i),i=window.setTimeout(()=>{t.call(this,...o)},e)}},tr=(t,e,i)=>{const o=t[e];t[e]=function(...t){o.call(this,...t),i.call(this,o,...t)}};(()=>{if("undefined"!=typeof window&&!("onscrollend"in window)){const t=new Set,e=new WeakMap,i=e=>{for(const i of e.changedTouches)t.add(i.identifier)},o=e=>{for(const i of e.changedTouches)t.delete(i.identifier)};document.addEventListener("touchstart",i,!0),document.addEventListener("touchend",o,!0),document.addEventListener("touchcancel",o,!0),tr(EventTarget.prototype,"addEventListener",function(i,o){if("scrollend"!==o)return;const s=Qs(()=>{t.size?s():this.dispatchEvent(new Event("scrollend"))},100);i.call(this,"scroll",s,{passive:!0}),e.set(this,s)}),tr(EventTarget.prototype,"removeEventListener",function(t,i){if("scrollend"!==i)return;const o=e.get(this);o&&t.call(this,"scroll",o,{passive:!0})})}})();var er=pt`
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
    -webkit-user-select: none;
    cursor: pointer;
    transition:
      var(--transition-speed) box-shadow,
      var(--transition-speed) color;
  }

  .tab:hover:not(.tab--disabled) {
    color: var(--sl-color-primary-600);
  }

  :host(:focus) {
    outline: transparent;
  }

  :host(:focus-visible) {
    color: var(--sl-color-primary-600);
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
`,ir=0,or=class extends We{constructor(){super(...arguments),this.localize=new to(this),this.attrId=++ir,this.componentId=`sl-tab-${this.attrId}`,this.panel="",this.active=!1,this.closable=!1,this.disabled=!1,this.tabIndex=0}connectedCallback(){super.connectedCallback(),this.setAttribute("role","tab")}handleCloseClick(t){t.stopPropagation(),this.emit("sl-close")}handleActiveChange(){this.setAttribute("aria-selected",this.active?"true":"false")}handleDisabledChange(){this.setAttribute("aria-disabled",this.disabled?"true":"false"),this.disabled&&!this.active?this.tabIndex=-1:this.tabIndex=0}render(){return this.id=this.id.length>0?this.id:this.componentId,Xt`
      <div
        part="base"
        class=${$i({tab:!0,"tab--active":this.active,"tab--closable":this.closable,"tab--disabled":this.disabled})}
      >
        <slot></slot>
        ${this.closable?Xt`
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
    `}};or.styles=[De,er],or.dependencies={"sl-icon-button":Pi},Le([Ve(".tab")],or.prototype,"tab",2),Le([He({reflect:!0})],or.prototype,"panel",2),Le([He({type:Boolean,reflect:!0})],or.prototype,"active",2),Le([He({type:Boolean,reflect:!0})],or.prototype,"closable",2),Le([He({type:Boolean,reflect:!0})],or.prototype,"disabled",2),Le([He({type:Number,reflect:!0})],or.prototype,"tabIndex",2),Le([Re("active")],or.prototype,"handleActiveChange",1),Le([Re("disabled")],or.prototype,"handleDisabledChange",1),or.define("sl-tab");var sr=pt`
  :host {
    --padding: 0;

    display: none;
  }

  :host([active]) {
    display: block;
  }

  .tab-panel {
    display: block;
    padding: var(--padding);
  }
`,rr=0,nr=class extends We{constructor(){super(...arguments),this.attrId=++rr,this.componentId=`sl-tab-panel-${this.attrId}`,this.name="",this.active=!1}connectedCallback(){super.connectedCallback(),this.id=this.id.length>0?this.id:this.componentId,this.setAttribute("role","tabpanel")}handleActiveChange(){this.setAttribute("aria-hidden",this.active?"false":"true")}render(){return Xt`
      <slot
        part="base"
        class=${$i({"tab-panel":!0,"tab-panel--active":this.active})}
      ></slot>
    `}};nr.styles=[De,sr],Le([He({reflect:!0})],nr.prototype,"name",2),Le([He({type:Boolean,reflect:!0})],nr.prototype,"active",2),Le([Re("active")],nr.prototype,"handleActiveChange",1),nr.define("sl-tab-panel");var ar=pt`
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
    -webkit-user-select: none;
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
    line-height: var(--sl-line-height-dense);
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
    flex-shrink: 0;
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
`,lr=pt`
  :host {
    display: inline-block;
  }

  .checkbox {
    position: relative;
    display: inline-flex;
    align-items: flex-start;
    font-family: var(--sl-input-font-family);
    font-weight: var(--sl-input-font-weight);
    color: var(--sl-input-label-color);
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
    transition:
      var(--sl-transition-fast) border-color,
      var(--sl-transition-fast) background-color,
      var(--sl-transition-fast) color,
      var(--sl-transition-fast) box-shadow;
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
    -webkit-user-select: none;
  }

  :host([required]) .checkbox__label::after {
    content: var(--sl-input-required-content);
    color: var(--sl-input-required-content-color);
    margin-inline-start: var(--sl-input-required-content-offset);
  }
`,cr=pt`
  .form-control .form-control__label {
    display: none;
  }

  .form-control .form-control__help-text {
    display: none;
  }

  /* Label */
  .form-control--has-label .form-control__label {
    display: inline-block;
    color: var(--sl-input-label-color);
    margin-bottom: var(--sl-spacing-3x-small);
  }

  .form-control--has-label.form-control--small .form-control__label {
    font-size: var(--sl-input-label-font-size-small);
  }

  .form-control--has-label.form-control--medium .form-control__label {
    font-size: var(--sl-input-label-font-size-medium);
  }

  .form-control--has-label.form-control--large .form-control__label {
    font-size: var(--sl-input-label-font-size-large);
  }

  :host([required]) .form-control--has-label .form-control__label::after {
    content: var(--sl-input-required-content);
    margin-inline-start: var(--sl-input-required-content-offset);
    color: var(--sl-input-required-content-color);
  }

  /* Help text */
  .form-control--has-help-text .form-control__help-text {
    display: block;
    color: var(--sl-input-help-text-color);
    margin-top: var(--sl-spacing-3x-small);
  }

  .form-control--has-help-text.form-control--small .form-control__help-text {
    font-size: var(--sl-input-help-text-font-size-small);
  }

  .form-control--has-help-text.form-control--medium .form-control__help-text {
    font-size: var(--sl-input-help-text-font-size-medium);
  }

  .form-control--has-help-text.form-control--large .form-control__help-text {
    font-size: var(--sl-input-help-text-font-size-large);
  }

  .form-control--has-help-text.form-control--radio-group .form-control__help-text {
    margin-top: var(--sl-spacing-2x-small);
  }
`,dr=new WeakMap,hr=new WeakMap,ur=new WeakMap,pr=new WeakSet,br=new WeakMap,fr=class{constructor(t,e){this.handleFormData=t=>{const e=this.options.disabled(this.host),i=this.options.name(this.host),o=this.options.value(this.host),s="sl-button"===this.host.tagName.toLowerCase();this.host.isConnected&&!e&&!s&&"string"==typeof i&&i.length>0&&void 0!==o&&(Array.isArray(o)?o.forEach(e=>{t.formData.append(i,e.toString())}):t.formData.append(i,o.toString()))},this.handleFormSubmit=t=>{var e;const i=this.options.disabled(this.host),o=this.options.reportValidity;this.form&&!this.form.noValidate&&(null==(e=dr.get(this.form))||e.forEach(t=>{this.setUserInteracted(t,!0)})),!this.form||this.form.noValidate||i||o(this.host)||(t.preventDefault(),t.stopImmediatePropagation())},this.handleFormReset=()=>{this.options.setValue(this.host,this.options.defaultValue(this.host)),this.setUserInteracted(this.host,!1),br.set(this.host,[])},this.handleInteraction=t=>{const e=br.get(this.host);e.includes(t.type)||e.push(t.type),e.length===this.options.assumeInteractionOn.length&&this.setUserInteracted(this.host,!0)},this.checkFormValidity=()=>{if(this.form&&!this.form.noValidate){const t=this.form.querySelectorAll("*");for(const e of t)if("function"==typeof e.checkValidity&&!e.checkValidity())return!1}return!0},this.reportFormValidity=()=>{if(this.form&&!this.form.noValidate){const t=this.form.querySelectorAll("*");for(const e of t)if("function"==typeof e.reportValidity&&!e.reportValidity())return!1}return!0},(this.host=t).addController(this),this.options=Pe({form:t=>{const e=t.form;if(e){const i=t.getRootNode().querySelector(`#${e}`);if(i)return i}return t.closest("form")},name:t=>t.name,value:t=>t.value,defaultValue:t=>t.defaultValue,disabled:t=>{var e;return null!=(e=t.disabled)&&e},reportValidity:t=>"function"!=typeof t.reportValidity||t.reportValidity(),checkValidity:t=>"function"!=typeof t.checkValidity||t.checkValidity(),setValue:(t,e)=>t.value=e,assumeInteractionOn:["sl-input"]},e)}hostConnected(){const t=this.options.form(this.host);t&&this.attachForm(t),br.set(this.host,[]),this.options.assumeInteractionOn.forEach(t=>{this.host.addEventListener(t,this.handleInteraction)})}hostDisconnected(){this.detachForm(),br.delete(this.host),this.options.assumeInteractionOn.forEach(t=>{this.host.removeEventListener(t,this.handleInteraction)})}hostUpdated(){const t=this.options.form(this.host);t||this.detachForm(),t&&this.form!==t&&(this.detachForm(),this.attachForm(t)),this.host.hasUpdated&&this.setValidity(this.host.validity.valid)}attachForm(t){t?(this.form=t,dr.has(this.form)?dr.get(this.form).add(this.host):dr.set(this.form,new Set([this.host])),this.form.addEventListener("formdata",this.handleFormData),this.form.addEventListener("submit",this.handleFormSubmit),this.form.addEventListener("reset",this.handleFormReset),hr.has(this.form)||(hr.set(this.form,this.form.reportValidity),this.form.reportValidity=()=>this.reportFormValidity()),ur.has(this.form)||(ur.set(this.form,this.form.checkValidity),this.form.checkValidity=()=>this.checkFormValidity())):this.form=void 0}detachForm(){if(!this.form)return;const t=dr.get(this.form);t&&(t.delete(this.host),t.size<=0&&(this.form.removeEventListener("formdata",this.handleFormData),this.form.removeEventListener("submit",this.handleFormSubmit),this.form.removeEventListener("reset",this.handleFormReset),hr.has(this.form)&&(this.form.reportValidity=hr.get(this.form),hr.delete(this.form)),ur.has(this.form)&&(this.form.checkValidity=ur.get(this.form),ur.delete(this.form)),this.form=void 0))}setUserInteracted(t,e){e?pr.add(t):pr.delete(t),t.requestUpdate()}doAction(t,e){if(this.form){const i=document.createElement("button");i.type=t,i.style.position="absolute",i.style.width="0",i.style.height="0",i.style.clipPath="inset(50%)",i.style.overflow="hidden",i.style.whiteSpace="nowrap",e&&(i.name=e.name,i.value=e.value,["formaction","formenctype","formmethod","formnovalidate","formtarget"].forEach(t=>{e.hasAttribute(t)&&i.setAttribute(t,e.getAttribute(t))})),this.form.append(i),i.click(),i.remove()}}getForm(){var t;return null!=(t=this.form)?t:null}reset(t){this.doAction("reset",t)}submit(t){this.doAction("submit",t)}setValidity(t){const e=this.host,i=Boolean(pr.has(e)),o=Boolean(e.required);e.toggleAttribute("data-required",o),e.toggleAttribute("data-optional",!o),e.toggleAttribute("data-invalid",!t),e.toggleAttribute("data-valid",t),e.toggleAttribute("data-user-invalid",!t&&i),e.toggleAttribute("data-user-valid",t&&i)}updateValidity(){const t=this.host;this.setValidity(t.validity.valid)}emitInvalidEvent(t){const e=new CustomEvent("sl-invalid",{bubbles:!1,composed:!1,cancelable:!0,detail:{}});t||e.preventDefault(),this.host.dispatchEvent(e)||null==t||t.preventDefault()}},mr=Object.freeze({badInput:!1,customError:!1,patternMismatch:!1,rangeOverflow:!1,rangeUnderflow:!1,stepMismatch:!1,tooLong:!1,tooShort:!1,typeMismatch:!1,valid:!0,valueMissing:!1});Object.freeze(Ie(Pe({},mr),{valid:!1,valueMissing:!0})),Object.freeze(Ie(Pe({},mr),{valid:!1,customError:!0}));const gr=_i(class extends xi{constructor(t){if(super(t),3!==t.type&&1!==t.type&&4!==t.type)throw Error("The `live` directive is not allowed on child or event bindings");if(!(t=>void 0===t.strings)(t))throw Error("`live` bindings can only contain a single expression")}render(t){return t}update(t,[e]){if(e===te||e===ee)return e;const i=t.element,o=t.name;if(3===t.type){if(e===i[o])return te}else if(4===t.type){if(!!e===i.hasAttribute(o))return te}else if(1===t.type&&i.getAttribute(o)===e+"")return te;return((t,e=fi)=>{t._$AH=e})(t),e}});var vr=class extends We{constructor(){super(...arguments),this.formControlController=new fr(this,{value:t=>t.checked?t.value||"on":void 0,defaultValue:t=>t.defaultChecked,setValue:(t,e)=>t.checked=e}),this.hasSlotController=new Mi(this,"help-text"),this.hasFocus=!1,this.title="",this.name="",this.size="medium",this.disabled=!1,this.checked=!1,this.indeterminate=!1,this.defaultChecked=!1,this.form="",this.required=!1,this.helpText=""}get validity(){return this.input.validity}get validationMessage(){return this.input.validationMessage}firstUpdated(){this.formControlController.updateValidity()}handleClick(){this.checked=!this.checked,this.indeterminate=!1,this.emit("sl-change")}handleBlur(){this.hasFocus=!1,this.emit("sl-blur")}handleInput(){this.emit("sl-input")}handleInvalid(t){this.formControlController.setValidity(!1),this.formControlController.emitInvalidEvent(t)}handleFocus(){this.hasFocus=!0,this.emit("sl-focus")}handleDisabledChange(){this.formControlController.setValidity(this.disabled)}handleStateChange(){this.input.checked=this.checked,this.input.indeterminate=this.indeterminate,this.formControlController.updateValidity()}click(){this.input.click()}focus(t){this.input.focus(t)}blur(){this.input.blur()}checkValidity(){return this.input.checkValidity()}getForm(){return this.formControlController.getForm()}reportValidity(){return this.input.reportValidity()}setCustomValidity(t){this.input.setCustomValidity(t),this.formControlController.updateValidity()}render(){const t=this.hasSlotController.test("help-text"),e=!!this.helpText||!!t;return Xt`
      <div
        class=${$i({"form-control":!0,"form-control--small":"small"===this.size,"form-control--medium":"medium"===this.size,"form-control--large":"large"===this.size,"form-control--has-help-text":e})}
      >
        <label
          part="base"
          class=${$i({checkbox:!0,"checkbox--checked":this.checked,"checkbox--disabled":this.disabled,"checkbox--focused":this.hasFocus,"checkbox--indeterminate":this.indeterminate,"checkbox--small":"small"===this.size,"checkbox--medium":"medium"===this.size,"checkbox--large":"large"===this.size})}
        >
          <input
            class="checkbox__input"
            type="checkbox"
            title=${this.title}
            name=${this.name}
            value=${zi(this.value)}
            .indeterminate=${gr(this.indeterminate)}
            .checked=${gr(this.checked)}
            .disabled=${this.disabled}
            .required=${this.required}
            aria-checked=${this.checked?"true":"false"}
            aria-describedby="help-text"
            @click=${this.handleClick}
            @input=${this.handleInput}
            @invalid=${this.handleInvalid}
            @blur=${this.handleBlur}
            @focus=${this.handleFocus}
          />

          <span
            part="control${this.checked?" control--checked":""}${this.indeterminate?" control--indeterminate":""}"
            class="checkbox__control"
          >
            ${this.checked?Xt`
                  <sl-icon part="checked-icon" class="checkbox__checked-icon" library="system" name="check"></sl-icon>
                `:""}
            ${!this.checked&&this.indeterminate?Xt`
                  <sl-icon
                    part="indeterminate-icon"
                    class="checkbox__indeterminate-icon"
                    library="system"
                    name="indeterminate"
                  ></sl-icon>
                `:""}
          </span>

          <div part="label" class="checkbox__label">
            <slot></slot>
          </div>
        </label>

        <div
          aria-hidden=${e?"false":"true"}
          class="form-control__help-text"
          id="help-text"
          part="form-control-help-text"
        >
          <slot name="help-text">${this.helpText}</slot>
        </div>
      </div>
    `}};vr.styles=[De,cr,lr],vr.dependencies={"sl-icon":wi},Le([Ve('input[type="checkbox"]')],vr.prototype,"input",2),Le([Ue()],vr.prototype,"hasFocus",2),Le([He()],vr.prototype,"title",2),Le([He()],vr.prototype,"name",2),Le([He()],vr.prototype,"value",2),Le([He({reflect:!0})],vr.prototype,"size",2),Le([He({type:Boolean,reflect:!0})],vr.prototype,"disabled",2),Le([He({type:Boolean,reflect:!0})],vr.prototype,"checked",2),Le([He({type:Boolean,reflect:!0})],vr.prototype,"indeterminate",2),Le([((t="value")=>(e,i)=>{const o=e.constructor,s=o.prototype.attributeChangedCallback;o.prototype.attributeChangedCallback=function(e,r,n){var a;const l=o.getPropertyOptions(t);if(e===("string"==typeof l.attribute?l.attribute:t)){const e=l.converter||Ct,o=("function"==typeof e?e:null!=(a=null==e?void 0:e.fromAttribute)?a:Ct.fromAttribute)(n,l.type);this[t]!==o&&(this[i]=o)}s.call(this,e,r,n)}})("checked")],vr.prototype,"defaultChecked",2),Le([He({reflect:!0})],vr.prototype,"form",2),Le([He({type:Boolean,reflect:!0})],vr.prototype,"required",2),Le([He({attribute:"help-text"})],vr.prototype,"helpText",2),Le([Re("disabled",{waitUntilFirstUpdate:!0})],vr.prototype,"handleDisabledChange",1),Le([Re(["checked","indeterminate"],{waitUntilFirstUpdate:!0})],vr.prototype,"handleStateChange",1);var yr=pt`
  :host {
    --track-width: 2px;
    --track-color: rgb(128 128 128 / 25%);
    --indicator-color: var(--sl-color-primary-600);
    --speed: 2s;

    display: inline-flex;
    width: 1em;
    height: 1em;
    flex: none;
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
  }

  .spinner__indicator {
    stroke: var(--indicator-color);
    stroke-linecap: round;
    stroke-dasharray: 150% 75%;
    animation: spin var(--speed) linear infinite;
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
      stroke-dasharray: 0.05em, 3em;
    }

    50% {
      transform: rotate(450deg);
      stroke-dasharray: 1.375em, 1.375em;
    }

    100% {
      transform: rotate(1080deg);
      stroke-dasharray: 0.05em, 3em;
    }
  }
`,wr=class extends We{constructor(){super(...arguments),this.localize=new to(this)}render(){return Xt`
      <svg part="base" class="spinner" role="progressbar" aria-label=${this.localize.term("loading")}>
        <circle class="spinner__track"></circle>
        <circle class="spinner__indicator"></circle>
      </svg>
    `}};function _r(t,e,i){return t?e(t):i?.(t)}wr.styles=[De,yr];var xr=class t extends We{constructor(){super(...arguments),this.localize=new to(this),this.indeterminate=!1,this.isLeaf=!1,this.loading=!1,this.selectable=!1,this.expanded=!1,this.selected=!1,this.disabled=!1,this.lazy=!1}static isTreeItem(t){return t instanceof Element&&"treeitem"===t.getAttribute("role")}connectedCallback(){super.connectedCallback(),this.setAttribute("role","treeitem"),this.setAttribute("tabindex","-1"),this.isNestedItem()&&(this.slot="children")}firstUpdated(){this.childrenContainer.hidden=!this.expanded,this.childrenContainer.style.height=this.expanded?"auto":"0",this.isLeaf=!this.lazy&&0===this.getChildrenItems().length,this.handleExpandedChange()}async animateCollapse(){this.emit("sl-collapse"),await Hi(this.childrenContainer);const{keyframes:t,options:e}=Ri(this,"tree-item.collapse",{dir:this.localize.dir()});await Bi(this.childrenContainer,Ui(t,this.childrenContainer.scrollHeight),e),this.childrenContainer.hidden=!0,this.emit("sl-after-collapse")}isNestedItem(){const e=this.parentElement;return!!e&&t.isTreeItem(e)}handleChildrenSlotChange(){this.loading=!1,this.isLeaf=!this.lazy&&0===this.getChildrenItems().length}willUpdate(t){t.has("selected")&&!t.has("indeterminate")&&(this.indeterminate=!1)}async animateExpand(){this.emit("sl-expand"),await Hi(this.childrenContainer),this.childrenContainer.hidden=!1;const{keyframes:t,options:e}=Ri(this,"tree-item.expand",{dir:this.localize.dir()});await Bi(this.childrenContainer,Ui(t,this.childrenContainer.scrollHeight),e),this.childrenContainer.style.height="auto",this.emit("sl-after-expand")}handleLoadingChange(){this.setAttribute("aria-busy",this.loading?"true":"false"),this.loading||this.animateExpand()}handleDisabledChange(){this.setAttribute("aria-disabled",this.disabled?"true":"false")}handleSelectedChange(){this.setAttribute("aria-selected",this.selected?"true":"false")}handleExpandedChange(){this.isLeaf?this.removeAttribute("aria-expanded"):this.setAttribute("aria-expanded",this.expanded?"true":"false")}handleExpandAnimation(){this.expanded?this.lazy?(this.loading=!0,this.emit("sl-lazy-load")):this.animateExpand():this.animateCollapse()}handleLazyChange(){this.emit("sl-lazy-change")}getChildrenItems({includeDisabled:e=!0}={}){return this.childrenSlot?[...this.childrenSlot.assignedElements({flatten:!0})].filter(i=>t.isTreeItem(i)&&(e||!i.disabled)):[]}render(){const t="rtl"===this.localize.dir(),e=!this.loading&&(!this.isLeaf||this.lazy);return Xt`
      <div
        part="base"
        class="${$i({"tree-item":!0,"tree-item--expanded":this.expanded,"tree-item--selected":this.selected,"tree-item--disabled":this.disabled,"tree-item--leaf":this.isLeaf,"tree-item--has-expand-button":e,"tree-item--rtl":"rtl"===this.localize.dir()})}"
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
            class=${$i({"tree-item__expand-button":!0,"tree-item__expand-button--visible":e})}
            aria-hidden="true"
          >
            ${_r(this.loading,()=>Xt` <sl-spinner part="spinner" exportparts="base:spinner__base"></sl-spinner> `)}
            <slot class="tree-item__expand-icon-slot" name="expand-icon">
              <sl-icon library="system" name=${t?"chevron-left":"chevron-right"}></sl-icon>
            </slot>
            <slot class="tree-item__expand-icon-slot" name="collapse-icon">
              <sl-icon library="system" name=${t?"chevron-left":"chevron-right"}></sl-icon>
            </slot>
          </div>

          ${_r(this.selectable,()=>Xt`
              <sl-checkbox
                part="checkbox"
                exportparts="
                    base:checkbox__base,
                    control:checkbox__control,
                    control--checked:checkbox__control--checked,
                    control--indeterminate:checkbox__control--indeterminate,
                    checked-icon:checkbox__checked-icon,
                    indeterminate-icon:checkbox__indeterminate-icon,
                    label:checkbox__label
                  "
                class="tree-item__checkbox"
                ?disabled="${this.disabled}"
                ?checked="${gr(this.selected)}"
                ?indeterminate="${this.indeterminate}"
                tabindex="-1"
              ></sl-checkbox>
            `)}

          <slot class="tree-item__label" part="label"></slot>
        </div>

        <div class="tree-item__children" part="children" role="group">
          <slot name="children" @slotchange="${this.handleChildrenSlotChange}"></slot>
        </div>
      </div>
    `}};xr.styles=[De,ar],xr.dependencies={"sl-checkbox":vr,"sl-icon":wi,"sl-spinner":wr},Le([Ue()],xr.prototype,"indeterminate",2),Le([Ue()],xr.prototype,"isLeaf",2),Le([Ue()],xr.prototype,"loading",2),Le([Ue()],xr.prototype,"selectable",2),Le([He({type:Boolean,reflect:!0})],xr.prototype,"expanded",2),Le([He({type:Boolean,reflect:!0})],xr.prototype,"selected",2),Le([He({type:Boolean,reflect:!0})],xr.prototype,"disabled",2),Le([He({type:Boolean,reflect:!0})],xr.prototype,"lazy",2),Le([Ve("slot:not([name])")],xr.prototype,"defaultSlot",2),Le([Ve("slot[name=children]")],xr.prototype,"childrenSlot",2),Le([Ve(".tree-item__item")],xr.prototype,"itemElement",2),Le([Ve(".tree-item__children")],xr.prototype,"childrenContainer",2),Le([Ve(".tree-item__expand-button slot")],xr.prototype,"expandButtonSlot",2),Le([Re("loading",{waitUntilFirstUpdate:!0})],xr.prototype,"handleLoadingChange",1),Le([Re("disabled")],xr.prototype,"handleDisabledChange",1),Le([Re("selected")],xr.prototype,"handleSelectedChange",1),Le([Re("expanded",{waitUntilFirstUpdate:!0})],xr.prototype,"handleExpandedChange",1),Le([Re("expanded",{waitUntilFirstUpdate:!0})],xr.prototype,"handleExpandAnimation",1),Le([Re("lazy",{waitUntilFirstUpdate:!0})],xr.prototype,"handleLazyChange",1);var $r=xr;Fi("tree-item.expand",{keyframes:[{height:"0",opacity:"0",overflow:"hidden"},{height:"auto",opacity:"1",overflow:"hidden"}],options:{duration:250,easing:"cubic-bezier(0.4, 0.0, 0.2, 1)"}}),Fi("tree-item.collapse",{keyframes:[{height:"auto",opacity:"1",overflow:"hidden"},{height:"0",opacity:"0",overflow:"hidden"}],options:{duration:200,easing:"cubic-bezier(0.4, 0.0, 0.2, 1)"}});var kr=pt`
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

    /*
     * Tree item indentation uses the "em" unit to increment its width on each level, so setting the font size to zero
     * here removes the indentation for all the nodes on the first level.
     */
    font-size: 0;
  }
`;function Ar(t,e,i){return(t=>Object.is(t,-0)?0:t)(t<e?e:t>i?i:t)}function Cr(t,e=!1){function i(t){const e=t.getChildrenItems({includeDisabled:!1});if(e.length){const i=e.every(t=>t.selected),o=e.every(t=>!t.selected&&!t.indeterminate);t.selected=i,t.indeterminate=!i&&!o}}!function t(o){for(const i of o.getChildrenItems())i.selected=e?o.selected||i.selected:!i.disabled&&o.selected,t(i);e&&i(o)}(t),function t(e){const o=e.parentElement;$r.isTreeItem(o)&&(i(o),t(o))}(t)}var Er=class extends We{constructor(){super(),this.selection="single",this.clickTarget=null,this.localize=new to(this),this.initTreeItem=t=>{t.selectable="multiple"===this.selection,["expand","collapse"].filter(t=>!!this.querySelector(`[slot="${t}-icon"]`)).forEach(e=>{const i=t.querySelector(`[slot="${e}-icon"]`),o=this.getExpandButtonIcon(e);o&&(null===i?t.append(o):i.hasAttribute("data-default")&&i.replaceWith(o))})},this.handleTreeChanged=t=>{for(const e of t){const t=[...e.addedNodes].filter($r.isTreeItem),i=[...e.removedNodes].filter($r.isTreeItem);t.forEach(this.initTreeItem),this.lastFocusedItem&&i.includes(this.lastFocusedItem)&&(this.lastFocusedItem=null)}},this.handleFocusOut=t=>{const e=t.relatedTarget;e&&this.contains(e)||(this.tabIndex=0)},this.handleFocusIn=t=>{const e=t.target;t.target===this&&this.focusItem(this.lastFocusedItem||this.getAllTreeItems()[0]),$r.isTreeItem(e)&&!e.disabled&&(this.lastFocusedItem&&(this.lastFocusedItem.tabIndex=-1),this.lastFocusedItem=e,this.tabIndex=-1,e.tabIndex=0)},this.addEventListener("focusin",this.handleFocusIn),this.addEventListener("focusout",this.handleFocusOut),this.addEventListener("sl-lazy-change",this.handleSlotChange)}async connectedCallback(){super.connectedCallback(),this.setAttribute("role","tree"),this.setAttribute("tabindex","0"),await this.updateComplete,this.mutationObserver=new MutationObserver(this.handleTreeChanged),this.mutationObserver.observe(this,{childList:!0,subtree:!0})}disconnectedCallback(){var t;super.disconnectedCallback(),null==(t=this.mutationObserver)||t.disconnect()}getExpandButtonIcon(t){const e=("expand"===t?this.expandedIconSlot:this.collapsedIconSlot).assignedElements({flatten:!0})[0];if(e){const i=e.cloneNode(!0);return[i,...i.querySelectorAll("[id]")].forEach(t=>t.removeAttribute("id")),i.setAttribute("data-default",""),i.slot=`${t}-icon`,i}return null}selectItem(t){const e=[...this.selectedItems];if("multiple"===this.selection)t.selected=!t.selected,t.lazy&&(t.expanded=!0),Cr(t);else if("single"===this.selection||t.isLeaf){const e=this.getAllTreeItems();for(const i of e)i.selected=i===t}else"leaf"===this.selection&&(t.expanded=!t.expanded);const i=this.selectedItems;(e.length!==i.length||i.some(t=>!e.includes(t)))&&Promise.all(i.map(t=>t.updateComplete)).then(()=>{this.emit("sl-selection-change",{detail:{selection:i}})})}getAllTreeItems(){return[...this.querySelectorAll("sl-tree-item")]}focusItem(t){null==t||t.focus()}handleKeyDown(t){if(!["ArrowDown","ArrowUp","ArrowRight","ArrowLeft","Home","End","Enter"," "].includes(t.key))return;if(t.composedPath().some(t=>{var e;return["input","textarea"].includes(null==(e=null==t?void 0:t.tagName)?void 0:e.toLowerCase())}))return;const e=this.getFocusableItems(),i="ltr"===this.localize.dir(),o="rtl"===this.localize.dir();if(e.length>0){t.preventDefault();const s=e.findIndex(t=>t.matches(":focus")),r=e[s],n=t=>{const i=e[Ar(t,0,e.length-1)];this.focusItem(i)},a=t=>{r.expanded=t};"ArrowDown"===t.key?n(s+1):"ArrowUp"===t.key?n(s-1):i&&"ArrowRight"===t.key||o&&"ArrowLeft"===t.key?!r||r.disabled||r.expanded||r.isLeaf&&!r.lazy?n(s+1):a(!0):i&&"ArrowLeft"===t.key||o&&"ArrowRight"===t.key?!r||r.disabled||r.isLeaf||!r.expanded?n(s-1):a(!1):"Home"===t.key?n(0):"End"===t.key?n(e.length-1):"Enter"!==t.key&&" "!==t.key||r.disabled||this.selectItem(r)}}handleClick(t){const e=t.target,i=e.closest("sl-tree-item"),o=t.composedPath().some(t=>{var e;return null==(e=null==t?void 0:t.classList)?void 0:e.contains("tree-item__expand-button")});i&&!i.disabled&&e===this.clickTarget&&(o?i.expanded=!i.expanded:this.selectItem(i))}handleMouseDown(t){this.clickTarget=t.target}handleSlotChange(){this.getAllTreeItems().forEach(this.initTreeItem)}async handleSelectionChange(){const t="multiple"===this.selection,e=this.getAllTreeItems();this.setAttribute("aria-multiselectable",t?"true":"false");for(const i of e)i.selectable=t;t&&(await this.updateComplete,[...this.querySelectorAll(":scope > sl-tree-item")].forEach(t=>Cr(t,!0)))}get selectedItems(){return this.getAllTreeItems().filter(t=>t.selected)}getFocusableItems(){const t=this.getAllTreeItems(),e=new Set;return t.filter(t=>{var i;if(t.disabled)return!1;const o=null==(i=t.parentElement)?void 0:i.closest("[role=treeitem]");return o&&(!o.expanded||o.loading||e.has(o))&&e.add(t),!e.has(t)})}render(){return Xt`
      <div
        part="base"
        class="tree"
        @click=${this.handleClick}
        @keydown=${this.handleKeyDown}
        @mousedown=${this.handleMouseDown}
      >
        <slot @slotchange=${this.handleSlotChange}></slot>
        <span hidden aria-hidden="true"><slot name="expand-icon"></slot></span>
        <span hidden aria-hidden="true"><slot name="collapse-icon"></slot></span>
      </div>
    `}};Er.styles=[De,kr],Le([Ve("slot:not([name])")],Er.prototype,"defaultSlot",2),Le([Ve("slot[name=expand-icon]")],Er.prototype,"expandedIconSlot",2),Le([Ve("slot[name=collapse-icon]")],Er.prototype,"collapsedIconSlot",2),Le([He()],Er.prototype,"selection",2),Le([Re("selection")],Er.prototype,"handleSelectionChange",1),Er.define("sl-tree"),$r.define("sl-tree-item");var Sr=pt`
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
`,Tr=()=>null,zr=class extends We{constructor(){super(...arguments),this.isCollapsed=!1,this.localize=new to(this),this.positionBeforeCollapsing=0,this.position=50,this.vertical=!1,this.disabled=!1,this.snapValue="",this.snapFunction=Tr,this.snapThreshold=12}toSnapFunction(t){const e=t.split(" ");return({pos:i,size:o,snapThreshold:s,isRtl:r,vertical:n})=>{let a=i,l=Number.POSITIVE_INFINITY;return e.forEach(e=>{let c;if(e.startsWith("repeat(")){const e=t.substring(7,t.length-1),s=e.endsWith("%"),a=Number.parseFloat(e),l=s?o*(a/100):a;c=Math.round((r&&!n?o-i:i)/l)*l}else c=e.endsWith("%")?o*(Number.parseFloat(e)/100):Number.parseFloat(e);r&&!n&&(c=o-c);const d=Math.abs(i-c);d<=s&&d<l&&(a=c,l=d)}),a}}set snap(t){this.snapValue=null!=t?t:"",this.snapFunction=t?"string"==typeof t?this.toSnapFunction(t):t:Tr}get snap(){return this.snapValue}connectedCallback(){super.connectedCallback(),this.resizeObserver=new ResizeObserver(t=>this.handleResize(t)),this.updateComplete.then(()=>this.resizeObserver.observe(this)),this.detectSize(),this.cachedPositionInPixels=this.percentageToPixels(this.position)}disconnectedCallback(){var t;super.disconnectedCallback(),null==(t=this.resizeObserver)||t.unobserve(this)}detectSize(){const{width:t,height:e}=this.getBoundingClientRect();this.size=this.vertical?e:t}percentageToPixels(t){return this.size*(t/100)}pixelsToPercentage(t){return t/this.size*100}handleDrag(t){const e="rtl"===this.localize.dir();this.disabled||(t.cancelable&&t.preventDefault(),function(t,e){function i(i){const o=t.getBoundingClientRect(),s=t.ownerDocument.defaultView,r=o.left+s.scrollX,n=o.top+s.scrollY,a=i.pageX-r,l=i.pageY-n;(null==e?void 0:e.onMove)&&e.onMove(a,l)}document.addEventListener("pointermove",i,{passive:!0}),document.addEventListener("pointerup",function t(){document.removeEventListener("pointermove",i),document.removeEventListener("pointerup",t),(null==e?void 0:e.onStop)&&e.onStop()}),(null==e?void 0:e.initialEvent)instanceof PointerEvent&&i(e.initialEvent)}(this,{onMove:(t,i)=>{var o;let s=this.vertical?i:t;"end"===this.primary&&(s=this.size-s),s=null!=(o=this.snapFunction({pos:s,size:this.size,snapThreshold:this.snapThreshold,isRtl:e,vertical:this.vertical}))?o:s,this.position=Ar(this.pixelsToPercentage(s),0,100)},initialEvent:t}))}handleKeyDown(t){if(!this.disabled&&["ArrowLeft","ArrowRight","ArrowUp","ArrowDown","Home","End","Enter"].includes(t.key)){let e=this.position;const i=(t.shiftKey?10:1)*("end"===this.primary?-1:1);if(t.preventDefault(),("ArrowLeft"===t.key&&!this.vertical||"ArrowUp"===t.key&&this.vertical)&&(e-=i),("ArrowRight"===t.key&&!this.vertical||"ArrowDown"===t.key&&this.vertical)&&(e+=i),"Home"===t.key&&(e="end"===this.primary?100:0),"End"===t.key&&(e="end"===this.primary?0:100),"Enter"===t.key)if(this.isCollapsed)e=this.positionBeforeCollapsing,this.isCollapsed=!1;else{const t=this.position;e=0,requestAnimationFrame(()=>{this.isCollapsed=!0,this.positionBeforeCollapsing=t})}this.position=Ar(e,0,100)}}handleResize(t){const{width:e,height:i}=t[0].contentRect;this.size=this.vertical?i:e,(isNaN(this.cachedPositionInPixels)||this.position===1/0)&&(this.cachedPositionInPixels=Number(this.getAttribute("position-in-pixels")),this.positionInPixels=Number(this.getAttribute("position-in-pixels")),this.position=this.pixelsToPercentage(this.positionInPixels)),this.primary&&(this.position=this.pixelsToPercentage(this.cachedPositionInPixels))}handlePositionChange(){this.cachedPositionInPixels=this.percentageToPixels(this.position),this.isCollapsed=!1,this.positionBeforeCollapsing=0,this.positionInPixels=this.percentageToPixels(this.position),this.emit("sl-reposition")}handlePositionInPixelsChange(){this.position=this.pixelsToPercentage(this.positionInPixels)}handleVerticalChange(){this.detectSize()}render(){const t=this.vertical?"gridTemplateRows":"gridTemplateColumns",e=this.vertical?"gridTemplateColumns":"gridTemplateRows",i="rtl"===this.localize.dir(),o=`\n      clamp(\n        0%,\n        clamp(\n          var(--min),\n          ${this.position}% - var(--divider-width) / 2,\n          var(--max)\n        ),\n        calc(100% - var(--divider-width))\n      )\n    `,s="auto";return"end"===this.primary?i&&!this.vertical?this.style[t]=`${o} var(--divider-width) ${s}`:this.style[t]=`${s} var(--divider-width) ${o}`:i&&!this.vertical?this.style[t]=`${s} var(--divider-width) ${o}`:this.style[t]=`${o} var(--divider-width) ${s}`,this.style[e]="",Xt`
      <slot name="start" part="panel start" class="start"></slot>

      <div
        part="divider"
        class="divider"
        tabindex=${zi(this.disabled?void 0:"0")}
        role="separator"
        aria-valuenow=${this.position}
        aria-valuemin="0"
        aria-valuemax="100"
        aria-label=${this.localize.term("resize")}
        @keydown=${this.handleKeyDown}
        @mousedown=${this.handleDrag}
        @touchstart=${this.handleDrag}
      >
        <slot name="divider"></slot>
      </div>

      <slot name="end" part="panel end" class="end"></slot>
    `}};zr.styles=[De,Sr],Le([Ve(".divider")],zr.prototype,"divider",2),Le([He({type:Number,reflect:!0})],zr.prototype,"position",2),Le([He({attribute:"position-in-pixels",type:Number})],zr.prototype,"positionInPixels",2),Le([He({type:Boolean,reflect:!0})],zr.prototype,"vertical",2),Le([He({type:Boolean,reflect:!0})],zr.prototype,"disabled",2),Le([He()],zr.prototype,"primary",2),Le([He({reflect:!0})],zr.prototype,"snap",1),Le([He({type:Number,attribute:"snap-threshold"})],zr.prototype,"snapThreshold",2),Le([Re("position")],zr.prototype,"handlePositionChange",1),Le([Re("positionInPixels")],zr.prototype,"handlePositionInPixelsChange",1),Le([Re("vertical")],zr.prototype,"handleVerticalChange",1),zr.define("sl-split-panel");var Pr=pt`
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
    -webkit-user-select: none;
    white-space: nowrap;
    vertical-align: middle;
    padding: 0;
    transition:
      var(--sl-transition-x-fast) background-color,
      var(--sl-transition-x-fast) color,
      var(--sl-transition-x-fast) border,
      var(--sl-transition-x-fast) box-shadow;
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

  /* When disabled, prevent mouse events from bubbling up from children */
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
    border-color: var(--sl-input-border-color);
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
    border-color: var(--sl-input-border-color);
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
    height: auto;
    min-height: var(--sl-input-height-small);
    font-size: var(--sl-button-font-size-small);
    line-height: calc(var(--sl-input-height-small) - var(--sl-input-border-width) * 2);
    border-radius: var(--sl-input-border-radius-small);
  }

  .button--medium {
    height: auto;
    min-height: var(--sl-input-height-medium);
    font-size: var(--sl-button-font-size-medium);
    line-height: calc(var(--sl-input-height-medium) - var(--sl-input-border-width) * 2);
    border-radius: var(--sl-input-border-radius-medium);
  }

  .button--large {
    height: auto;
    min-height: var(--sl-input-height-large);
    font-size: var(--sl-button-font-size-large);
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

  :host([data-sl-button-group__button--first]:not([data-sl-button-group__button--last])) .button {
    border-start-end-radius: 0;
    border-end-end-radius: 0;
  }

  :host([data-sl-button-group__button--inner]) .button {
    border-radius: 0;
  }

  :host([data-sl-button-group__button--last]:not([data-sl-button-group__button--first])) .button {
    border-start-start-radius: 0;
    border-end-start-radius: 0;
  }

  /* All except the first */
  :host([data-sl-button-group__button]:not([data-sl-button-group__button--first])) {
    margin-inline-start: calc(-1 * var(--sl-input-border-width));
  }

  /* Add a visual separator between solid buttons */
  :host(
      [data-sl-button-group__button]:not(
          [data-sl-button-group__button--first],
          [data-sl-button-group__button--radio],
          [variant='default']
        ):not(:hover)
    )
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
  :host([data-sl-button-group__button--hover]) {
    z-index: 1;
  }

  /* Focus and checked are always on top */
  :host([data-sl-button-group__button--focus]),
  :host([data-sl-button-group__button][checked]) {
    z-index: 2;
  }
`,Ir=class extends We{constructor(){super(...arguments),this.formControlController=new fr(this,{assumeInteractionOn:["click"]}),this.hasSlotController=new Mi(this,"[default]","prefix","suffix"),this.localize=new to(this),this.hasFocus=!1,this.invalid=!1,this.title="",this.variant="default",this.size="medium",this.caret=!1,this.disabled=!1,this.loading=!1,this.outline=!1,this.pill=!1,this.circle=!1,this.type="button",this.name="",this.value="",this.href="",this.rel="noreferrer noopener"}get validity(){return this.isButton()?this.button.validity:mr}get validationMessage(){return this.isButton()?this.button.validationMessage:""}firstUpdated(){this.isButton()&&this.formControlController.updateValidity()}handleBlur(){this.hasFocus=!1,this.emit("sl-blur")}handleFocus(){this.hasFocus=!0,this.emit("sl-focus")}handleClick(){"submit"===this.type&&this.formControlController.submit(this),"reset"===this.type&&this.formControlController.reset(this)}handleInvalid(t){this.formControlController.setValidity(!1),this.formControlController.emitInvalidEvent(t)}isButton(){return!this.href}isLink(){return!!this.href}handleDisabledChange(){this.isButton()&&this.formControlController.setValidity(this.disabled)}click(){this.button.click()}focus(t){this.button.focus(t)}blur(){this.button.blur()}checkValidity(){return!this.isButton()||this.button.checkValidity()}getForm(){return this.formControlController.getForm()}reportValidity(){return!this.isButton()||this.button.reportValidity()}setCustomValidity(t){this.isButton()&&(this.button.setCustomValidity(t),this.formControlController.updateValidity())}render(){const t=this.isLink(),e=t?Ci`a`:Ci`button`;return Ti`
      <${e}
        part="base"
        class=${$i({button:!0,"button--default":"default"===this.variant,"button--primary":"primary"===this.variant,"button--success":"success"===this.variant,"button--neutral":"neutral"===this.variant,"button--warning":"warning"===this.variant,"button--danger":"danger"===this.variant,"button--text":"text"===this.variant,"button--small":"small"===this.size,"button--medium":"medium"===this.size,"button--large":"large"===this.size,"button--caret":this.caret,"button--circle":this.circle,"button--disabled":this.disabled,"button--focused":this.hasFocus,"button--loading":this.loading,"button--standard":!this.outline,"button--outline":this.outline,"button--pill":this.pill,"button--rtl":"rtl"===this.localize.dir(),"button--has-label":this.hasSlotController.test("[default]"),"button--has-prefix":this.hasSlotController.test("prefix"),"button--has-suffix":this.hasSlotController.test("suffix")})}
        ?disabled=${zi(t?void 0:this.disabled)}
        type=${zi(t?void 0:this.type)}
        title=${this.title}
        name=${zi(t?void 0:this.name)}
        value=${zi(t?void 0:this.value)}
        href=${zi(t&&!this.disabled?this.href:void 0)}
        target=${zi(t?this.target:void 0)}
        download=${zi(t?this.download:void 0)}
        rel=${zi(t?this.rel:void 0)}
        role=${zi(t?void 0:"button")}
        aria-disabled=${this.disabled?"true":"false"}
        tabindex=${this.disabled?"-1":"0"}
        @blur=${this.handleBlur}
        @focus=${this.handleFocus}
        @invalid=${this.isButton()?this.handleInvalid:null}
        @click=${this.handleClick}
      >
        <slot name="prefix" part="prefix" class="button__prefix"></slot>
        <slot part="label" class="button__label"></slot>
        <slot name="suffix" part="suffix" class="button__suffix"></slot>
        ${this.caret?Ti` <sl-icon part="caret" class="button__caret" library="system" name="caret"></sl-icon> `:""}
        ${this.loading?Ti`<sl-spinner part="spinner"></sl-spinner>`:""}
      </${e}>
    `}};Ir.styles=[De,Pr],Ir.dependencies={"sl-icon":wi,"sl-spinner":wr},Le([Ve(".button")],Ir.prototype,"button",2),Le([Ue()],Ir.prototype,"hasFocus",2),Le([Ue()],Ir.prototype,"invalid",2),Le([He()],Ir.prototype,"title",2),Le([He({reflect:!0})],Ir.prototype,"variant",2),Le([He({reflect:!0})],Ir.prototype,"size",2),Le([He({type:Boolean,reflect:!0})],Ir.prototype,"caret",2),Le([He({type:Boolean,reflect:!0})],Ir.prototype,"disabled",2),Le([He({type:Boolean,reflect:!0})],Ir.prototype,"loading",2),Le([He({type:Boolean,reflect:!0})],Ir.prototype,"outline",2),Le([He({type:Boolean,reflect:!0})],Ir.prototype,"pill",2),Le([He({type:Boolean,reflect:!0})],Ir.prototype,"circle",2),Le([He()],Ir.prototype,"type",2),Le([He()],Ir.prototype,"name",2),Le([He()],Ir.prototype,"value",2),Le([He()],Ir.prototype,"href",2),Le([He()],Ir.prototype,"target",2),Le([He()],Ir.prototype,"rel",2),Le([He()],Ir.prototype,"download",2),Le([He()],Ir.prototype,"form",2),Le([He({attribute:"formaction"})],Ir.prototype,"formAction",2),Le([He({attribute:"formenctype"})],Ir.prototype,"formEnctype",2),Le([He({attribute:"formmethod"})],Ir.prototype,"formMethod",2),Le([He({attribute:"formnovalidate",type:Boolean})],Ir.prototype,"formNoValidate",2),Le([He({attribute:"formtarget"})],Ir.prototype,"formTarget",2),Le([Re("disabled",{waitUntilFirstUpdate:!0})],Ir.prototype,"handleDisabledChange",1),Ir.define("sl-button"),wr.define("sl-spinner");class Lr extends nt{static styles=r`
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
    `;static properties={path:{type:String},_dialogOpened:{type:Boolean,state:!0},_visible:{type:Boolean,state:!0}};connectedCallback(){super.connectedCallback(),this.observer=new IntersectionObserver((t,e)=>{t.forEach(t=>{t.isIntersecting?this._visible=!0:this._visible=!1})}),this.observer.observe(this.parentElement)}disconnectedCallback(){super.disconnectedCallback(),this.observer.disconnect()}constructor(){super(),this._visible=!1,this._dialogOpened=!1}hideLoading(t,e){this.renderRoot.querySelector(`#${t}`).remove(),this.renderRoot.querySelector(`#${e}`).style.height="85vh"}openFullscreen(){const t=this.renderRoot.querySelector(".dialog-overview");if(!t)throw Error("failed to find dialog element, unable to open fullscreen diagram view.");return this._dialogOpened=!0,t.show()}spinnerTemplate(t){return N`
            <div id=${t} class="loading">
                <sl-spinner></sl-spinner>
            </div>
        `}iframeTemplate(t,e){return N`
            ${this.spinnerTemplate(t)}
            <iframe id=${e} seamless frameborder="0" scrolling="no" class="plot-iframe"
                @load=${()=>this.hideLoading(t,e)} src=${this.path}>
            </iframe>
        `}dialogTemplate(){return N`
            <sl-dialog class="dialog-overview">
                ${this._dialogOpened?this.iframeTemplate("dialog-spinner","dialog-iframe"):N``}
            </sl-dialog>
        `}render(){return this._visible?N`
            <sl-divider></sl-divider>

            <div style="display: flex;flex-direction: column;align-items: flex-end;">
                ${this.dialogTemplate()}
                <sl-button style="margin-right: 2em;" @click=${this.openFullscreen}>
                    Open Fullscreen View
                </sl-button>
            </div>

            ${this.iframeTemplate("page-spinner","page-iframe")}
        `:N``}}customElements.define("sc-diagram",Lr);var Or=pt`
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
    -webkit-user-select: none;
    cursor: pointer;
  }

  .details__header::-webkit-details-marker {
    display: none;
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
`,Fr=class extends We{constructor(){super(...arguments),this.localize=new to(this),this.open=!1,this.disabled=!1}firstUpdated(){this.body.style.height=this.open?"auto":"0",this.open&&(this.details.open=!0),this.detailsObserver=new MutationObserver(t=>{for(const e of t)"attributes"===e.type&&"open"===e.attributeName&&(this.details.open?this.show():this.hide())}),this.detailsObserver.observe(this.details,{attributes:!0})}disconnectedCallback(){var t;super.disconnectedCallback(),null==(t=this.detailsObserver)||t.disconnect()}handleSummaryClick(t){t.preventDefault(),this.disabled||(this.open?this.hide():this.show(),this.header.focus())}handleSummaryKeyDown(t){"Enter"!==t.key&&" "!==t.key||(t.preventDefault(),this.open?this.hide():this.show()),"ArrowUp"!==t.key&&"ArrowLeft"!==t.key||(t.preventDefault(),this.hide()),"ArrowDown"!==t.key&&"ArrowRight"!==t.key||(t.preventDefault(),this.show())}async handleOpenChange(){if(this.open){if(this.details.open=!0,this.emit("sl-show",{cancelable:!0}).defaultPrevented)return this.open=!1,void(this.details.open=!1);await Hi(this.body);const{keyframes:t,options:e}=Ri(this,"details.show",{dir:this.localize.dir()});await Bi(this.body,Ui(t,this.body.scrollHeight),e),this.body.style.height="auto",this.emit("sl-after-show")}else{if(this.emit("sl-hide",{cancelable:!0}).defaultPrevented)return this.details.open=!0,void(this.open=!0);await Hi(this.body);const{keyframes:t,options:e}=Ri(this,"details.hide",{dir:this.localize.dir()});await Bi(this.body,Ui(t,this.body.scrollHeight),e),this.body.style.height="auto",this.details.open=!1,this.emit("sl-after-hide")}}async show(){if(!this.open&&!this.disabled)return this.open=!0,Di(this,"sl-after-show")}async hide(){if(this.open&&!this.disabled)return this.open=!1,Di(this,"sl-after-hide")}render(){const t="rtl"===this.localize.dir();return Xt`
      <details
        part="base"
        class=${$i({details:!0,"details--open":this.open,"details--disabled":this.disabled,"details--rtl":t})}
      >
        <summary
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
        </summary>

        <div class="details__body" role="region" aria-labelledby="header">
          <slot part="content" id="content" class="details__content"></slot>
        </div>
      </details>
    `}};Fr.styles=[De,Or],Fr.dependencies={"sl-icon":wi},Le([Ve(".details")],Fr.prototype,"details",2),Le([Ve(".details__header")],Fr.prototype,"header",2),Le([Ve(".details__body")],Fr.prototype,"body",2),Le([Ve(".details__expand-icon-slot")],Fr.prototype,"expandIconSlot",2),Le([He({type:Boolean,reflect:!0})],Fr.prototype,"open",2),Le([He()],Fr.prototype,"summary",2),Le([He({type:Boolean,reflect:!0})],Fr.prototype,"disabled",2),Le([Re("open",{waitUntilFirstUpdate:!0})],Fr.prototype,"handleOpenChange",1),Fi("details.show",{keyframes:[{height:"0",opacity:"0"},{height:"auto",opacity:"1"}],options:{duration:250,easing:"linear"}}),Fi("details.hide",{keyframes:[{height:"auto",opacity:"1"},{height:"0",opacity:"0"}],options:{duration:250,easing:"linear"}}),Fr.define("sl-details");class Rr extends nt{static styles=r`
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
    `;static properties={title:{type:String},files:{type:Object},paths:{type:Object},loadedFiles:{type:Boolean,attribute:!1},diff:{type:String},diffFile:{type:Object}};getNewTabBtnTemplate(t){return N`
            <sl-button style="padding: var(--sl-spacing-x-small)" variant="primary" href=${URL.createObjectURL(t)} target="_blank">
                Open in New Tab
            </sl-button>
        `}getDiffTemplate(){if(this.diffFile){const t=`${this.title}-diff`;return N`
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
            `}return N``}getTabTemplate(t,e){const i=`details-panel-${this.title}-${t}`;return N`
            <sl-tab class="tab" slot="nav" panel=${i}>${t}</sl-tab>
            <sl-tab-panel class="tab-panel" name=${i}>
                <div class="text-field-container">
                    <div>
                        ${this.getNewTabBtnTemplate(e)}
                    </div>
                    <pre><code>${Ms(e.text(),N`Loading...`)}</code></pre>
                </div>
            </sl-tab-panel>
        `}async loadFiles(){for(const t of Object.entries(this.paths))await fetch(t[1]).then(t=>t.blob()).then(e=>{this.files[t[0]]=e});this.diff&&await fetch(this.diff).then(t=>t.blob()).then(t=>{this.diffFile=t}),this.loadedFiles=!0}connectedCallback(){super.connectedCallback(),!this.files&&this.paths?(this.files={},this.loadedFiles=!1,this.loadFiles()):this.loadedFiles=!0}render(){return this.files?N`
            <sl-details summary=${this.title}>
                <sl-tab-group>
                    ${Object.entries(this.files).map(t=>this.getTabTemplate(t[0],t[1]))}
                    ${this.getDiffTemplate()}
                </sl-tab-group>
            </sl-details>
        `:N``}}customElements.define("sc-file-preview",Rr);class Dr{}const Br=new WeakMap,Nr=Ts(class extends Ds{render(t){return U}update(t,[e]){var i;const o=e!==this.G;return o&&void 0!==this.G&&this.ot(void 0),(o||this.rt!==this.lt)&&(this.G=e,this.dt=null===(i=t.options)||void 0===i?void 0:i.host,this.ot(this.lt=t.element)),U}ot(t){var e;if("function"==typeof this.G){const i=null!==(e=this.dt)&&void 0!==e?e:globalThis;let o=Br.get(i);void 0===o&&(o=new WeakMap,Br.set(i,o)),void 0!==o.get(this.G)&&this.G.call(this.dt,void 0),o.set(this.G,t),void 0!==t&&this.G.call(this.dt,t)}else this.G.value=t}get rt(){var t,e,i;return"function"==typeof this.G?null===(e=Br.get(null!==(t=this.dt)&&void 0!==t?t:globalThis))||void 0===e?void 0:e.get(this.G):null===(i=this.G)||void 0===i?void 0:i.value}disconnected(){this.rt===this.lt&&this.ot(void 0)}reconnected(){this.ot(this.lt)}});class Hr extends js{static styles=[js.styles,r`
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
        `];tableRef=(()=>new Dr)();removeDetailsEl(t){for(const e of t.childNodes)if("TR"===e.tagName)for(const t of e.childNodes)for(const e of t.childNodes)"SL-DETAILS"===e.tagName&&t.removeChild(e);return t}copyTable(){const t=window.getSelection();t.removeAllRanges();const e=document.createRange();e.selectNodeContents(this.tableRef.value),t.addRange(e),this.removeDetailsEl(t.anchorNode),document.execCommand("copy"),t.removeAllRanges(),this.requestUpdate()}parseMetric(t){const e=t[0].split("|");return N`
            <td rowspan=${t[1]}>
                <strong>${e[0]}</strong>
                <sl-details summary="Description">
                    ${e[1]}
                </sl-details>
            </td>
        `}parseSummaryFunc(t){const[e,i]=t.split("|");return N`
            <td class="td-value">
                ${i?N`<abbr title=${i}>${e}</abbr>`:N`${e}`}
            </td>
        `}async parseSrc(){let t,e=N``;for await(const i of this.makeTextFileLineIterator(this.file)){const o=i.split(";"),s=o[0];if(o.shift(),"H"===s)for(const t of o)e=N`${e}<th>${t}</th>`,this.cols=this.cols+1;else if("M"===s)t=this.parseMetric(o);else{const i=N`${o.map(t=>this.parseSummaryFunc(t))}`;e=N`
                    ${e}
                    <tr>
                      ${t}
                      ${i}
                    </tr>
                `,t&&(t=void 0)}}return e=N`<table ${Nr(this.tableRef)} width=${this.getWidth(this.cols)}>${e}</table>`,N`
            <div style="display:flex;">
                ${e}
                <sl-button style="margin-left:5px" @click=${this.copyTable}>Copy table</sl-button>
            </div>
        `}constructor(){super(),this.cols=0}connectedCallback(){super.connectedCallback(),this.parseSrc().then(t=>{this.template=t})}}customElements.define("sc-smry-tbl",Hr);class Ur extends nt{static styles=r`
        sl-alert {
            margin-left: 20px;
            margin-right: 20px;
        }
  `;static properties={paths:{type:Array},alerts:{type:Array},fpreviews:{type:Array},smrytblpath:{type:String},smrytblfile:{type:Blob}};summaryTableTemplate(){return N`
            <div style="margin-left: 2em; margin-right: 1em;">
                <sc-smry-tbl .file="${this.smrytblfile}"></sc-smry-tbl>
            </div>
        `}render(){return this.smrytblpath&&!this.smrytblfile&&fetch(this.smrytblpath).then(t=>t.blob()).then(t=>{this.smrytblfile=t}),N`
            <br>
            ${this.smrytblfile?this.summaryTableTemplate():N``}

            ${this.alerts.length>0?N`
                    <br>
                    <sl-alert variant="primary" open>
                        <ul>
                            ${this.alerts.map(t=>N`<li>${t}</li>`)}
                        </ul>
                    </sl-alert>
                    <br>
                `:N``}

            ${this.fpreviews?this.fpreviews.map(t=>N`
                    <sc-file-preview .title=${t.title}
                        .diff=${t.diff} .diffFile=${t.diffFile}
                        .paths=${t.paths} .files=${t.files}>
                    </sc-file-preview>
                    <br>
                `):N``}
            <div style="display: flex; flex-direction: column;">
                ${this.paths?this.paths.map(t=>N`<sc-diagram path=${t}></sc-diagram>`):N``}
            </div>
        `}}customElements.define("sc-data-tab",Ur),customElements.define("sc-tab-panel",class extends nt{static properties={tab:{type:Object}};selectTabInTabTree(t){const e=this.renderRoot.querySelectorAll("sl-tree-item[selected]");for(const t of e)t.selected=!1;const i=this.renderRoot.querySelectorAll("sl-tree-item[expanded]");for(const t of i)t.expanded=!1;let o=this.renderRoot.getElementById(`${t}-tree`);for(o.selected=!0;"SL-TREE-ITEM"===o.tagName;)o.expanded=!0,o=o.parentElement}hasDataTab(t){return this.dataTabs.includes(t)}show(t){if(!this.hasDataTab(t))return;if(this.activeDataTab?.id===t)return;this.activeDataTab&&(this.activeDataTab.hidden=!0);const e=this.renderRoot.getElementById(t);this.activeDataTab=e,e&&(e.hidden=!1),this.selectTabInTabTree(t)}tabPanesTemplate(t){let e=N``;for(const i of t.tabs)e=i.tabs?N`${e}${this.tabPanesTemplate(i)}`:N`${e}
                    <sc-data-tab hidden id=${i.id} tabname=${i.name}
                        .smrytblpath=${i.smrytblpath} .smrytblfile=${i.smrytblfile}
                        .paths=${i.ppaths} .fpreviews=${i.fpreviews}
                        .dir=${i.dir} .alerts=${i.alerts}>
                    </sc-data-tab>`;return e}firstUpdated(){this.show(this.firstTab)}treeItemTemplate(t){return t.tabs?N`
            ${t.name}
            ${t.tabs.map(t=>N`
                    <sl-tree-item id=${`${t.id}-tree`} @click=${t.tabs?()=>{}:()=>{location.hash=t.id}}>
                        ${this.treeItemTemplate(t)}
                    </sl-tree-item>
                `)}
        `:(this.dataTabs.push(t.id),this.firstTab||(this.firstTab=t.id),t.name)}render(){return this.tab?N`
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
        `:N``}constructor(){super(),this.dataTabs=[],this.firstTab=""}});class Mr extends nt{static styles=r`
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
    `;static properties={tabs:{type:Object}};get _tabPanels(){return this.renderRoot.querySelectorAll("sc-tab-panel")}get _tabGroup(){return this.renderRoot.querySelector("sl-tab-group")}getTabPanel(t){for(const e of this._tabPanels)if(e.hasDataTab(t))return e}getActiveTab(){const t=this._tabGroup.querySelectorAll("sl-tab");for(const e of t)if(e.active)return e;throw Error("BUG: unable to find active tab")}getActiveDataTab(){const t=this.getActiveTab();for(const e of this._tabPanels)if(e.tab.name===t.panel)return e.activeDataTab;throw Error("BUG: unable to find active data tab")}show(t=location.hash.substring(1)){for(const e of this._tabPanels)e.show(t)}firstUpdated(){this.tabChangeHandler=()=>{location.href=`#${this.getActiveDataTab().id}`},this._tabGroup.addEventListener("sl-tab-show",this.tabChangeHandler),this._tabGroup.updateComplete.then(()=>{const t=location.hash.substring(1);if(!t)return void(location.hash=`${this._tabPanels[0].firstTab}`);const e=this.getTabPanel(t);e.updateComplete.then(()=>{e.show(t),this._tabGroup.show(e.parentElement.name)})})}connectedCallback(){super.connectedCallback(),this.hashHandler=()=>{this.show()},window.addEventListener("hashchange",this.hashHandler,!1)}disconnectedCallback(){window.removeEventListener("hashchange",this.hashHandler),this._tabGroup.removeEventListener("sl-tab-show",this.tabChangeHandler)}render(){return this.tabs?N`
            <sl-tab-group>
                ${this.tabs.map(t=>N`
                    <sl-tab class="tab" slot="nav" panel="${t.name}">${t.name}</sl-tab>
                    <sl-tab-panel class="tab-panel" name="${t.name}">
                        <sc-tab-panel .tab=${t}></sc-tab-panel>
                    </sl-tab-panel>
                `)}
            </sl-tab-group>
      `:N``}}function Vr(t){return t.replace(/\s/g,"-").replace("%","Percent").replace(/[^a-zA-Z0-9-]+/g,"")}customElements.define("sc-tab-group",Mr);class jr extends nt{static properties={introtbl:{type:Object},src:{type:String},reportInfo:{type:Object},toolname:{type:String},titleDescr:{type:String},tabs:{type:Object},fetchFailed:{type:Boolean,attribute:!1}};static styles=r`
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
    `;get _corsWarning(){return this.renderRoot.querySelector(".cors-warning")}initRepProps(){this.reportTitle=this.reportInfo.title,this.reportDescr=this.reportInfo.descr,this.toolname=this.reportInfo.toolname,this.toolver=this.reportInfo.toolver,this.logPath=this.reportInfo.logpath}generateTabIDs(t){for(const e of t){e.tabs&&(e.tabs=this.generateTabIDs(e.tabs));const t=Vr(e.name);this.tabIDs.has(t)?(this.tabIDs.set(t,this.tabIDs.get(t)+1),e.id=`${t}-${this.tabIDs.get(t)}`):(this.tabIDs.set(t,0),e.id=t)}return t}parseReportInfo(t){this.reportInfo=t,this.initRepProps(),t.intro_tbl&&fetch(t.intro_tbl).then(t=>t.blob()).then(t=>{this.introtbl=t}),fetch(t.tab_file).then(t=>t.json()).then(async t=>{this.tabs=this.generateTabIDs(t)})}connectedCallback(){fetch(this.src).then(t=>t.json()).then(t=>this.parseReportInfo(t)).catch(t=>{if(!(t instanceof TypeError))throw t;this.fetchFailed=!0}),super.connectedCallback()}firstUpdated(){const t=this.renderRoot.querySelector(".report-info-dialog");this.renderRoot.querySelector(".open-info-dialog").addEventListener("click",()=>t.show())}updated(t){t.has("fetchFailed")&&this.fetchFailed&&this._corsWarning.addEventListener("sl-request-close",t=>{t.preventDefault()})}corsWarning(){return N`
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
        `}findFile(t){const e=Object.keys(this.files);for(const i of e)if(i.endsWith(t))return this.files[i];throw Error(`unable to find an uploaded file ending with '${t}'.`)}async resolveTabFile(t,e){return t?await fetch(e).then(t=>t.blob()):this.findFile(e)}async extractTabs(t,e){for(const i of t){if(i.smrytblpath&&(i.smrytblfile=await this.resolveTabFile(e,i.smrytblpath)),i.fpreviews)for(const t of i.fpreviews){t.files={};for(const[i,o]of Object.entries(t.paths))t.files[i]=await this.resolveTabFile(e,o);t.diff&&(t.diffFile=await this.resolveTabFile(e,t.diff))}i.tabs&&(i.tabs=await this.extractTabs(i.tabs,e))}return this.generateTabIDs(t)}async processUploadedFiles(){const t=this.renderRoot.getElementById("upload-files");this.files={};for(const e of t.files)this.files[e.webkitRelativePath]=e;const e=await this.findFile("report_info.json").arrayBuffer();this.reportInfo=JSON.parse((new TextDecoder).decode(e)),this.introtbl=this.findFile(this.reportInfo.intro_tbl);const i=await this.findFile(this.reportInfo.tab_file).arrayBuffer().then(t=>JSON.parse((new TextDecoder).decode(t)));this.tabs=await this.extractTabs(i,!1),this.initRepProps(),this.fetchFailed=!1}constructor(){super(),this.fetchFailed=!1,this.reportInfo={},this.tabIDs=new Map,this.headerExpanded=!0}toggleHeader(){const t=this.renderRoot.querySelector(".report-head");this.headerExpanded?t.style.maxHeight="0vh":t.style.maxHeight="100vh",this.headerExpanded=!this.headerExpanded}reportInfoTemplate(){return N`
        <sl-dialog class="report-info-dialog" label="Report Info">
            ${this.toolname&&this.toolver?N`Generated with <i>'${this.toolname} v${this.toolver}'</i>`:N``}
            <br>
            <br>
            ${this.logPath?N`<u><i><a target="_blank" href=${this.logPath}>Report Generation Log</a></i></u>`:N``}
        </sl-dialog>
        `}render(){return this.fetchFailed?this.corsWarning():N`
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
                    ${this.reportTitle?N`<h1>${this.reportTitle}</h1>`:N``}
                    ${this.reportDescr?N`<p>${this.reportDescr}</p>`:N``}
                    ${this.introtbl?N`<sc-intro-tbl .file=${this.introtbl}></sc-intro-tbl>`:N``}
                </div>
            </div>
            <div class="sticky">
                <sl-button size="small" class="toggle-header-btn" @click=${this.toggleHeader}>
                    Toggle Header
                </sl-button>
                ${this.tabs?N`<sc-tab-group .tabs=${this.tabs}></sc-tab-group>`:N``}
            </div>
        `}}customElements.define("sc-report-page",jr),ai("shoelace")})();