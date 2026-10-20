export function ManualVerification({type}: {type:'image'|'video'}) {
  const prompts=type==='image' ? [
    ['Source and provenance','Find the original upload and independently verify where and when the image was captured.'],
    ['Edges and geometry','Inspect face boundaries, reflections, text, hands, and repeated details at the original resolution.'],
    ['Lighting and context','Compare shadows, skin detail, perspective, and surrounding objects. Editing and compression can also cause inconsistencies.'],
    ['Independent comparison','Use other photographs from the same event and check for an earlier version.'],
  ] : [
    ['Original source','Verify the original upload, creator, date, and whether the clip is a concept trailer, edit, or disclosure-labelled generation.'],
    ['Motion and continuity','Inspect cuts, facial boundaries, hands, reflections, textures, and object stability across adjacent frames.'],
    ['Audio and lip-sync','Listen independently for edits or synthetic speech; compare mouth movement with the soundtrack.'],
    ['Independent footage','Compare with original footage from the same scene. Real footage can be mixed with generated shots.'],
  ];
  return <section className="mt-4 rounded-xl border border-gray-800 bg-[#12121f] p-4">
    <h3 className="text-sm font-semibold text-white">Manual verification</h3>
    <p className="text-[11px] text-gray-400 leading-5 mt-2 mb-3">Review prompts, not model findings. No single visible anomaly proves a deepfake.</p>
    <div className="space-y-3">{prompts.map(([title,body])=><label key={title} className="flex items-start gap-2.5 text-xs leading-5 text-gray-300 cursor-pointer"><input type="checkbox" className="mt-1 h-4 w-4 shrink-0 accent-cyan-400" /><span><strong className="text-white">{title}: </strong>{body}</span></label>)}</div>
  </section>;
}
