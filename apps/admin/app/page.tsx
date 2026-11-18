'use client';
import { useEffect, useState } from 'react';
import { AlertTriangle, BellRing, Boxes, Database, Gauge, Users } from 'lucide-react';
type Overview = { products:number; variants:number; prices:number; users:number; active_alerts:number; data_label:string };
const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000/api/v1';
const sections = ['商品','商品型号','规格定义','分类与品牌','价格来源','价格记录','数据质量','重复商品','评论数据','推荐规则','兼容规则','用户','提醒','系统日志'];
export default function Dashboard() {
  const [data,setData] = useState<Overview|null>(null); const [error,setError] = useState(false);
  useEffect(() => { fetch(`${API}/admin/overview`).then((r) => { if(!r.ok) throw new Error(); return r.json(); }).then(setData).catch(() => setError(true)); }, []);
  const cards = [{label:'产品',value:data?.products??'—',icon:Boxes},{label:'型号',value:data?.variants??'—',icon:Gauge},{label:'价格记录',value:data?.prices??'—',icon:Database},{label:'用户',value:data?.users??'—',icon:Users},{label:'活跃提醒',value:data?.active_alerts??'—',icon:BellRing}];
  return <main className="mx-auto min-h-screen max-w-7xl p-6 lg:p-10"><header className="mb-10 flex items-end justify-between"><div><p className="mb-2 text-sm font-bold tracking-[.2em] text-emerald-700">SMARTBUY CONTROL</p><h1 className="text-4xl font-black">数据运营台</h1><p className="mt-2 text-slate-500">产品、价格、匹配与质量治理</p></div><span className="rounded-full bg-amber-100 px-3 py-1 text-sm font-bold text-amber-800">演示数据</span></header>
  {error&&<div className="mb-6 flex gap-3 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-amber-900"><AlertTriangle size={20}/>API 未连接，请先启动 FastAPI 服务。</div>}
  <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">{cards.map(({label,value,icon:Icon})=><article key={label} className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm"><Icon className="mb-5 text-emerald-700"/><p className="text-sm text-slate-500">{label}</p><p className="mt-1 text-3xl font-black">{value}</p></article>)}</section>
  <section className="mt-8 rounded-3xl border border-slate-200 bg-white p-6"><h2 className="text-xl font-black">管理模块</h2><p className="mt-1 text-sm text-slate-500">当前版本提供数据总览；编辑工作流将在建立权限角色后开放。</p><div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">{sections.map((section,index)=><button key={section} disabled={index>5} className="rounded-2xl border border-slate-200 p-4 text-left font-bold enabled:hover:border-emerald-500 enabled:hover:bg-emerald-50 disabled:cursor-not-allowed disabled:text-slate-400">{section}<span className="mt-1 block text-xs font-normal">{index>5?'即将支持':'只读总览'}</span></button>)}</div></section></main>;
}
