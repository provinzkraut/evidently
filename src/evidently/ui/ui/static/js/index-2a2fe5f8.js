import{r as s}from"./vendor-da67081a.js";function S(e,o){window.dispatchEvent(new StorageEvent("storage",{key:e,newValue:o}))}function d(){const[e,o]=s.useState(!1),r=s.useRef(null),n=s.useCallback(()=>{o(!0)},[]),a=s.useCallback(()=>{o(!1)},[]);return[s.useCallback(t=>{var u;((u=r.current)==null?void 0:u.nodeType)===Node.ELEMENT_NODE&&(r.current.removeEventListener("mouseenter",n),r.current.removeEventListener("mouseleave",a)),(t==null?void 0:t.nodeType)===Node.ELEMENT_NODE&&(t.addEventListener("mouseenter",n),t.addEventListener("mouseleave",a)),r.current=t},[n,a]),e]}const l=(e,o)=>{const r=JSON.stringify(o);window.localStorage.setItem(e,r),S(e,r)},g=e=>{window.localStorage.removeItem(e),S(e,null)},i=e=>window.localStorage.getItem(e),f=e=>(window.addEventListener("storage",e),()=>window.removeEventListener("storage",e)),E=()=>{throw Error("useLocalStorage is a client-only hook")};function m(e,o){const r=()=>i(e),n=s.useSyncExternalStore(f,r,E),a=s.useCallback(c=>{try{const t=typeof c=="function"?c(JSON.parse(n)):c;t==null?g(e):l(e,t)}catch(t){console.warn(t)}},[e,n]);return s.useEffect(()=>{i(e)===null&&typeof o<"u"&&l(e,o)},[e,o]),[n?JSON.parse(n):o,a]}export{m as a,d as u};