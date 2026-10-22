(() => {
  const host = document.querySelector('#current-reproduction');
  const element = (tag, text) => {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    return node;
  };
  fetch('f_tier/current-followup/result.json').then(response => {
    if (!response.ok) throw Error(response.status);
    return response.json();
  }).then(data => {
    if (data.complete_original_reproduction !== false || data.baseline_F_PASS !== 34 ||
        data.A03.status !== 'RUNNING' || data.A06.status !== 'RUNNING') {
      throw Error('进展快照与当前验收范围不符');
    }
    host.replaceChildren(element('summary', 'A03 / A06 · 当前实验与未通过的门槛'));
    host.append(element('p', data.summary), element('p', '快照时间：' + data.updated_utc));
    host.append(element('h2', 'A03 · 两种机器人共用技能'));
    for (const row of data.A03.rows) {
      host.append(element('p', `${row.robot}：${row.native_callbacks} 次物理回调 / ${row.native_seconds.toFixed(3)} 秒，夹爪驱动 ${row.driver_median_rad.toFixed(3)} rad，指垫间距 ${row.pad_gap_mm[0].toFixed(2)}–${row.pad_gap_mm[1].toFixed(2)} mm。${row.scope}。`));
    }
    host.append(element('p', data.A03.changes), element('p', data.A03.remaining));
    for (const row of data.A03.failed_loaded_prerequisites) {
      host.append(element('p', `${row.robot} 原架前置：${row.failure}；持载样本 ${row.loaded_hold_samples}，样本内最低抬升 ${row.minimum_observed_loaded_lift_mm.toFixed(2)} mm，实际关节加速度超限 ${row.motion_exceedance_joint_steps.actual_acceleration} 个关节×物理步。${row.scope}。`));
    }
    host.append(element('h2', 'A06 · 真实视频到仿真示范'));
    const source = element('p', '真实输入：');
    const link = element('a', data.A06.source.title + ' · ' + data.A06.source.author);
    link.href = data.A06.source.url;
    source.append(link, document.createTextNode('（' + data.A06.source.license + '）'));
    host.append(source, element('p', data.A06.source.assumptions));
    const fluid = data.A06.fluid_initialization;
    host.append(element('p', `${fluid.scope}：${fluid.particle_count} 个粒子，${fluid.native_callbacks_including_initialization} 次回调 / ${fluid.native_seconds.toFixed(3)} 秒。粒子坐标实际变化，最终 ${fluid.final_ideal_cavity_inside_centers}/${fluid.particle_count} 个显示粒子中心位于理想瓶腔内；瓶身倾角 ${fluid.final_bottle_tilt_deg.toFixed(2)}°。${fluid.limitations}`));
    const contact = data.A06.contact_controls;
    host.append(element('p', `接触观测：静态支撑 ${contact.source_support_force_N.toFixed(5)} N，悬空手指 ${contact.suspended_finger_force_N.join(' / ')} N。${contact.scope}`));
    host.append(element('p', data.A06.failed_tracking.result), element('p', data.A06.remaining), element('p', data.A06.BC_boundary));
    const gallery = element('div');
    gallery.className = 'gallery-grid';
    for (const figure of data.figures) {
      if (!/^[a-z-]+\.png$/.test(figure.src)) throw Error('无效图路径');
      const card = element('figure');
      card.className = 'gallery-card';
      const image = element('img');
      image.src = 'f_tier/current-followup/' + figure.src;
      image.alt = figure.caption;
      image.loading = 'lazy';
      card.append(image, element('figcaption', figure.caption));
      gallery.append(card);
    }
    host.append(gallery);
    const provenance = element('p');
    for (const [title, path] of [['可下载的结果快照', 'result.json'], ['图像及改编资产署名', 'ATTRIBUTION.txt']]) {
      const anchor = element('a', title);
      anchor.href = 'f_tier/current-followup/' + path;
      provenance.append(anchor, document.createTextNode(' · '));
    }
    host.append(provenance);
  }).catch(error => {
    host.replaceChildren(element('summary', '当前实验快照读取失败'), element('p', String(error)));
  });
})();
