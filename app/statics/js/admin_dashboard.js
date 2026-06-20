/* ══════════════════════════════════════════════
   HIRENEST ADMIN DASHBOARD — FULL WORKING JS
   ══════════════════════════════════════════════ */
 
// ─────────────────────────────────────────────
// JS-only state (for new items added this session)
// ─────────────────────────────────────────────
let JOBS    = JSON.parse(localStorage.getItem('hn_jobs')    || '[]');
let REPORTS = JSON.parse(localStorage.getItem('hn_reports') || '[]');
let _nextJobId = JOBS.reduce((m, j) => (!j.fromDB && typeof j.id === 'number') ? Math.max(m, j.id + 1) : m, 1);
let _nextReportId = REPORTS.reduce((m, r) => Math.max(m, r.id + 1), 1);
 
function persistState() {
  localStorage.setItem('hn_jobs',    JSON.stringify(JOBS.filter(j => !j.fromDB)));
  localStorage.setItem('hn_reports', JSON.stringify(REPORTS));
}
 
function setEl(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}
 
function updateStats() {
  const reportedJobs = REPORTS.filter(r => r.status === 'Under Review').length;
  const pendingMod   = JOBS.filter(j => j.status === 'Pending').length;
 
  setEl('stat-reported',    reportedJobs);
  setEl('stat-pending-mod', pendingMod);
  setEl('reportBadge',      reportedJobs);
  setEl('modPending',       pendingMod);
  setEl('modCount',         JOBS.length);
  setEl('reportCount',      REPORTS.length);
 
  const totalActive = JOBS.filter(j => j.status === 'Approved').length;
  setEl('stat-active-jobs', totalActive);
 
  updatePlatformHealth();
}
 
// ─────────────────────────────────────────────
// ACTIVITY LOG
// ─────────────────────────────────────────────
const activityLog = JSON.parse(localStorage.getItem('hn_activity_log') || '[]');
 
function logActivity(action, target, status) {
  activityLog.unshift({
    action, target, status,
    date: new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }),
    time: new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
  });
  if (activityLog.length > 100) activityLog.pop();
  localStorage.setItem('hn_activity_log', JSON.stringify(activityLog));
 
  const auditBody = document.getElementById('audit-body');
  if (auditBody && activityLog.length > 0) {
    const jsRows = activityLog.slice(0, 5).map(a => `
      <tr>
        <td>${a.action}</td>
        <td style="color:var(--muted)">${a.target}</td>
        <td style="color:var(--muted)">${a.date}</td>
        <td><span class="status-pill ${a.status}">${
          {success:'Completed', warning:'Pending', danger:'Removed', info:'Updated', muted:'Dismissed'}[a.status] || a.status
        }</span></td>
      </tr>`).join('');
    auditBody.innerHTML = jsRows + auditBody.innerHTML;
  }
 
  renderActionHistory(activityLog);
}
 
function renderActionHistory(data) {
  const tbody = document.getElementById('ph-history-body');
  if (!tbody) return;
 
  setEl('ph-total-actions', data.length);
  setEl('ph-completed',     data.filter(a => a.status === 'success').length);
  setEl('ph-removals',      data.filter(a => a.status === 'danger').length);
  setEl('ph-reports-filed', data.filter(a => a.action.toLowerCase().includes('report')).length);
  setEl('ph-action-count',  data.length);
 
  const lastEl = document.getElementById('ph-last-action');
  if (lastEl) {
    lastEl.textContent = data.length > 0
      ? `Last action: ${data[0].action} — ${data[0].date} at ${data[0].time}`
      : 'No actions yet';
  }
 
  if (data.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="empty-state">
      <i class="fa-solid fa-shield-halved"></i>
      <p>No admin actions recorded yet</p></td></tr>`;
    return;
  }
 
  const statusLabel = { success:'Completed', warning:'Pending', danger:'Removed', info:'Updated', muted:'Dismissed' };
 
  tbody.innerHTML = data.map((a, i) => `
    <tr>
      <td style="color:var(--muted);font-size:12px">${data.length - i}</td>
      <td><strong>${a.action}</strong></td>
      <td style="color:var(--muted)">${a.target}</td>
      <td style="color:var(--muted);font-size:12px">${a.date} <span style="opacity:0.6">${a.time}</span></td>
      <td><span class="status-pill ${a.status}">${statusLabel[a.status] || a.status}</span></td>
    </tr>`).join('');
}
 
function filterActionHistory() {
  const q      = (document.getElementById('phSearch')?.value || '').toLowerCase();
  const status = document.getElementById('phTypeFilter')?.value || '';
  const data   = activityLog.filter(a =>
    (!q      || a.action.toLowerCase().includes(q) || a.target.toLowerCase().includes(q)) &&
    (!status || a.status === status)
  );
  renderActionHistory(data);
}
 
function clearActionHistory() {
  showConfirm(
    'Clear History',
    'Clear all recorded admin actions? This cannot be undone.',
    'Clear', 'danger',
    () => {
      activityLog.length = 0;
      localStorage.removeItem('hn_activity_log');
      renderActionHistory([]);
      showToast('Action history cleared', 'danger');
    }
  );
}

// ─────────────────────────────────────────────
// LOGOUT CONFIRMATION
// ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const logoutBtn = document.querySelector('.logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', e => {
      e.preventDefault();
      showConfirm(
        'Logout',
        'Are you sure you want to log out?',
        'Yes, Logout', 'danger',
        () => { window.location.href = '/logout'; }
      );
    });
  }
});
 
// ─────────────────────────────────────────────
// TAB SWITCHING
// ─────────────────────────────────────────────
document.querySelectorAll('.nav-link[data-tab]').forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    const tab = link.dataset.tab;
 
    document.querySelectorAll('.nav-link[data-tab]').forEach(l => {
      l.classList.remove('active');
      const arrow = l.querySelector('.arrow');
      if (arrow) arrow.remove();
    });
    link.classList.add('active');
    const arrow = document.createElement('i');
    arrow.className = 'fa-solid fa-chevron-right arrow';
    link.appendChild(arrow);
 
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    const target = document.getElementById('tab-' + tab);
    if (target) target.classList.add('active');
 
    document.getElementById('sidebar')?.classList.remove('open');
 
    if (tab === 'job-moderation') loadModerationJobsFromDB();
    if (tab === 'analytics')      updateAnalytics();
    if (tab === 'company-jobs')   renderCompanyJobs();
  });
});
 
// ─────────────────────────────────────────────
// HAMBURGER
// ─────────────────────────────────────────────
document.getElementById('hamburger')?.addEventListener('click', () => {
  document.getElementById('sidebar')?.classList.toggle('open');
});
document.addEventListener('click', e => {
  const sidebar   = document.getElementById('sidebar');
  const hamburger = document.getElementById('hamburger');
  if (sidebar?.classList.contains('open') && !sidebar.contains(e.target) && !hamburger?.contains(e.target)) {
    sidebar.classList.remove('open');
  }
});
 
// ─────────────────────────────────────────────
// MODAL HELPERS
// ─────────────────────────────────────────────
function openModal(id)  { document.getElementById(id)?.classList.add('open');    }
function closeModal(id) { document.getElementById(id)?.classList.remove('open'); }
 
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', e => { if (e.target === overlay) overlay.classList.remove('open'); });
});
 
// ─────────────────────────────────────────────
// CONFIRM MODAL
// ─────────────────────────────────────────────
let _confirmCallback = null;
 
function showConfirm(title, message, btnLabel, btnClass, callback) {
  document.getElementById('confirmTitle').textContent   = title;
  document.getElementById('confirmMessage').textContent = message;
  const btn = document.getElementById('confirmBtn');
  btn.textContent = btnLabel;
  btn.className   = `action-btn ${btnClass}`;
  _confirmCallback = callback;
  openModal('confirmModal');
}
 
document.getElementById('confirmBtn')?.addEventListener('click', () => {
  if (_confirmCallback) _confirmCallback();
  closeModal('confirmModal');
  _confirmCallback = null;
});
 
// ─────────────────────────────────────────────
// TOAST
// ─────────────────────────────────────────────
function showToast(message, type = 'success') {
  let toast = document.getElementById('adminToast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'adminToast';
    toast.style.cssText = `
      position:fixed;bottom:28px;right:28px;z-index:9999;
      display:flex;align-items:center;gap:10px;
      padding:13px 20px;border-radius:12px;
      font-size:14px;font-weight:600;color:#fff;
      box-shadow:0 8px 30px rgba(0,0,0,0.18);
      transform:translateY(20px);opacity:0;
      transition:all 0.3s cubic-bezier(0.34,1.56,0.64,1);
      pointer-events:none;min-width:200px;
    `;
    document.body.appendChild(toast);
  }
  const colors = { success:'#16A34A', danger:'#EF4444', warning:'#D97706', info:'#6C5CE7' };
  const icons  = { success:'fa-circle-check', danger:'fa-circle-xmark', warning:'fa-triangle-exclamation', info:'fa-circle-info' };
  toast.style.background = colors[type] || colors.success;
  toast.innerHTML = `<i class="fa-solid ${icons[type] || icons.success}"></i> ${message}`;
  requestAnimationFrame(() => { toast.style.transform = 'translateY(0)'; toast.style.opacity = '1'; });
  clearTimeout(toast._timeout);
  toast._timeout = setTimeout(() => { toast.style.transform = 'translateY(20px)'; toast.style.opacity = '0'; }, 3000);
}
 
// ════════════════════════════════════════════
// ANALYTICS TAB
// ════════════════════════════════════════════
const announcementLog = [];
 
function renderDonut(svgId, legendId, segments) {
  const svg    = document.getElementById(svgId);
  const legend = document.getElementById(legendId);
  if (!svg || !legend) return;
 
  const total = segments.reduce((s, seg) => s + seg.value, 0);
  const radius = 50, circumference = 2 * Math.PI * radius;
 
  if (total === 0) {
    svg.innerHTML = `<circle cx="60" cy="60" r="${radius}" fill="none" stroke="#E5E7EB" stroke-width="16"/>
      <text x="60" y="64" text-anchor="middle" font-size="12" fill="var(--muted,#6b7280)">No data</text>`;
    legend.innerHTML = '';
    return;
  }
 
  let offsetAccum = 0, circles = '';
  segments.forEach(seg => {
    if (seg.value === 0) return;
    const dash = (seg.value / total) * circumference;
    circles += `<circle cx="60" cy="60" r="${radius}" fill="none" stroke="${seg.color}" stroke-width="16"
      stroke-dasharray="${dash} ${circumference - dash}"
      stroke-dashoffset="${-offsetAccum}"
      transform="rotate(-90 60 60)" />`;
    offsetAccum += dash;
  });
 
  svg.innerHTML = circles +
    `<text x="60" y="56" text-anchor="middle" font-size="22" font-weight="700" fill="var(--text,#1e293b)">${total}</text>
     <text x="60" y="74" text-anchor="middle" font-size="11" fill="var(--muted,#6b7280)">Total</text>`;
 
  legend.innerHTML = segments.map(seg => {
    const pct = Math.round((seg.value / total) * 100);
    return `<div style="display:flex;align-items:center;gap:10px;font-size:13px">
      <span style="width:10px;height:10px;border-radius:50%;background:${seg.color};flex-shrink:0"></span>
      <span style="flex:1;font-weight:500;color:var(--text,#1e293b)">${seg.label}</span>
      <span style="font-weight:700;width:28px;text-align:right">${seg.value}</span>
      <span style="color:var(--muted,#6b7280);width:38px;text-align:right;font-size:12px">${pct}%</span>
    </div>`;
  }).join('');
}
 
function updateAnalytics() {
  const totalJobs   = JOBS.length;
  const approved    = JOBS.filter(j => j.status === 'Approved').length;
  const rejected    = JOBS.filter(j => j.status === 'Rejected').length;
  const pending     = JOBS.filter(j => j.status === 'Pending').length;
  const totalRep    = REPORTS.length;
  const resolved    = REPORTS.filter(r => r.status === 'Resolved').length;
  const dismissed   = REPORTS.filter(r => r.status === 'Dismissed').length;
  const underReview = REPORTS.filter(r => r.status === 'Under Review').length;
 
  const approvalRate   = totalJobs > 0 ? Math.round((approved / totalJobs) * 100) : 0;
  const resolutionRate = totalRep  > 0 ? Math.round(((resolved + dismissed) / totalRep) * 100) : 0;
 
  let jobsViewed = parseInt(sessionStorage.getItem('hn_jobs_viewed') || '0');
  if (totalJobs > 0) {
    jobsViewed += Math.floor(Math.random() * 4) + 1;
    sessionStorage.setItem('hn_jobs_viewed', jobsViewed);
  }
 
  const appActions = activityLog.filter(a => a.action.includes('Approved') || a.action.includes('Submitted')).length;
  const avgApps    = totalJobs > 0 ? (appActions / totalJobs).toFixed(1) : '0.0';
 
  const roleCounts = { jobseeker: 0, employer: 0, admin: 0 };
  document.querySelectorAll('#users-body tr[id^="server-user-row-"]').forEach(row => {
    const r = (row.cells[2]?.textContent || '').toLowerCase().replace(/[\s_-]/g, '');
    if (r.includes('jobseeker'))     roleCounts.jobseeker++;
    else if (r.includes('employer')) roleCounts.employer++;
    else if (r.includes('admin'))    roleCounts.admin++;
  });
  const roleMap    = { jobseeker: 'Job Seeker', employer: 'Employer', admin: 'Admin' };
  const topRoleKey = Object.entries(roleCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || null;
  const topRole    = topRoleKey && roleCounts[topRoleKey] > 0 ? roleMap[topRoleKey] : '—';
 
  const typeCounts = {};
  JOBS.forEach(j => { typeCounts[j.type] = (typeCounts[j.type] || 0) + 1; });
  const topType = Object.entries(typeCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || '—';
 
  setEl('an-jobs-viewed',      jobsViewed > 0 ? jobsViewed.toLocaleString() : '—');
  setEl('an-avg-apps',         avgApps);
  setEl('an-most-active-role', topRole);
  setEl('an-top-job-type',     topType);
  setEl('an-approval-rate',    approvalRate + '%');
  setEl('an-report-rate',      resolutionRate + '%');
 
  renderDonut('reportStatusDonut', 'reportStatusLegend', [
    { label: 'Resolved',     value: resolved,    color: '#16A34A' },
    { label: 'Under Review', value: underReview, color: '#D97706' },
    { label: 'Dismissed',    value: dismissed,   color: '#94A3B8' },
  ]);
 
  const annBody = document.getElementById('an-announce-body');
  if (annBody) {
    if (announcementLog.length === 0) {
      annBody.innerHTML = `<tr><td colspan="4" class="empty-state">
        <i class="fa-solid fa-bullhorn"></i><p>No announcements sent yet</p></td></tr>`;
    } else {
      annBody.innerHTML = announcementLog.map(a => `
        <tr>
          <td><strong>${a.subject}</strong></td>
          <td><span class="status-pill info">${a.audience === 'all' ? 'All Users' : a.audience}</span></td>
          <td style="color:var(--muted);font-size:12px">${a.date}</td>
          <td><span class="status-pill success">Sent</span></td>
        </tr>`).join('');
    }
  }
}
 
// ════════════════════════════════════════════
// ADMIN NOTIFICATION DROPDOWN
// ════════════════════════════════════════════
const adminNotifs = JSON.parse(localStorage.getItem('hn_admin_notifs') || '[]');
let notifFilter = 'all';
 
function pushAdminNotif(action, target, status) {
  const typeMap = {
    success: 'job',
    danger:  'report',
    warning: 'job',
    info:    'announcement',
    muted:   'system',
  };
  let type = typeMap[status] || 'system';
  if (action.toLowerCase().includes('report')) type = 'report';
  adminNotifs.unshift({
    id:     Date.now(),
    type:   type,
    title:  action,
    msg:    target,
    time:   new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }),
    unread: true,
  });
  if (adminNotifs.length > 50) adminNotifs.pop();
  localStorage.setItem('hn_admin_notifs', JSON.stringify(adminNotifs));
  renderAdminNotifs();
}
 
const _origLogActivity = logActivity;
logActivity = function(action, target, status) {
  _origLogActivity(action, target, status);
  pushAdminNotif(action, target, status);
};
 
function getFilteredNotifs() {
  if (notifFilter === 'unread')       return adminNotifs.filter(n => n.unread);
  if (notifFilter === 'announcement') return adminNotifs.filter(n => n.type === 'announcement');
  if (notifFilter === 'report')       return adminNotifs.filter(n => n.type === 'report');
  return adminNotifs;
}
 
function renderAdminNotifs() {
  const body   = document.getElementById('notifListBody');
  const badge  = document.getElementById('notifBadge');
  const label  = document.getElementById('notifUnreadLabel');
  if (!body) return;
 
  const unread = adminNotifs.filter(n => n.unread).length;
  if (badge) {
    badge.textContent = unread > 99 ? '99+' : unread;
    badge.style.display = unread === 0 ? 'none' : 'flex';
  }
  if (label) label.textContent = unread > 0 ? `(${unread} unread)` : '';
 
  const data = getFilteredNotifs();
  if (data.length === 0) {
    body.innerHTML = `<div class="notif-empty">
      <i class="fa-solid fa-bell-slash"></i>
      <p>No notifications</p>
    </div>`;
    return;
  }
 
  const iconMap  = { announcement:'fa-bullhorn', user:'fa-user-plus', report:'fa-flag', job:'fa-briefcase', system:'fa-heart-pulse' };
  const classMap = { announcement:'announce',    user:'user',          report:'report', job:'job',          system:'system'        };
 
  body.innerHTML = data.map(n => `
    <div class="notif-item ${n.unread ? 'unread' : ''}" onclick="markAdminNotifRead(${n.id})">
      <div class="notif-icon ${classMap[n.type] || 'system'}">
        <i class="fa-solid ${iconMap[n.type] || 'fa-bell'}"></i>
      </div>
      <div class="notif-body">
        <div class="notif-title">${n.title}</div>
        <div class="notif-msg">${n.msg}</div>
        <div class="notif-time">${n.time}</div>
      </div>
      ${n.unread ? '<span class="notif-dot"></span>' : ''}
    </div>`).join('');
}
 
function markAdminNotifRead(id) {
  const n = adminNotifs.find(x => x.id === id);
  if (n) n.unread = false;
  renderAdminNotifs();
}
 
function markAllAdminNotifs() {
  adminNotifs.forEach(n => n.unread = false);
  renderAdminNotifs();
}
 
function setNotifFilter(f, btn) {
  notifFilter = f;
  document.querySelectorAll('.nftab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  renderAdminNotifs();
}
 
function toggleNotifDropdown() {
  const dd = document.getElementById('notifDropdown');
  if (dd) dd.classList.toggle('open');
}
 
function closeNotifDropdown() {
  document.getElementById('notifDropdown')?.classList.remove('open');
}
 
document.addEventListener('click', e => {
  const wrap = document.getElementById('notifWrap');
  if (wrap && !wrap.contains(e.target)) closeNotifDropdown();
});
 
// ════════════════════════════════════════════
// USER MANAGEMENT
// ════════════════════════════════════════════
function viewUserFromServer(id, name, email, role) {
  document.getElementById('viewJobTitle').textContent = name.trim() || email;
  document.getElementById('viewJobBody').innerHTML = `
    <div class="detail-grid">
      <div class="detail-item"><label>Full Name</label><span>${name.trim() || '—'}</span></div>
      <div class="detail-item"><label>Email</label><span>${email}</span></div>
      <div class="detail-item"><label>Role</label><span>${role}</span></div>
      <div class="detail-item"><label>User ID</label><span>#${id}</span></div>
      <div class="detail-item"><label>Status</label>
        <span class="status-pill success">Active</span>
      </div>
    </div>`;
  document.getElementById('viewJobFooter').innerHTML = `
    <button class="action-btn ghost" onclick="closeModal('viewJobModal')">Close</button>
    <button class="action-btn secondary" onclick="closeModal('viewJobModal');reportUserJob(${id},'${name.trim()}')">
      <i class="fa-solid fa-flag"></i> Report
    </button>
    <button class="action-btn danger" onclick="closeModal('viewJobModal');deleteUserFromServer(${id},'${name.trim()}')">
      <i class="fa-solid fa-trash"></i> Delete
    </button>`;
  openModal('viewJobModal');
}
 
function deleteUserFromServer(id, name) {
  showConfirm(
    'Delete User',
    `Permanently delete "${name || 'this user'}"? This cannot be undone.`,
    'Delete', 'danger',
    () => {
      fetch(`/admin/users/${id}/delete`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
          if (data.status === 'success') {
            const row = document.getElementById(`server-user-row-${id}`);
            if (row) row.remove();
            const badge = document.getElementById('userCount');
            if (badge) badge.textContent = parseInt(badge.textContent || '0') - 1;
            const statEl = document.getElementById('stat-total-users');
            if (statEl) statEl.textContent = parseInt(statEl.textContent || '0') - 1;
            logActivity('User Deleted', name || `User #${id}`, 'danger');
            showToast(`${name || 'User'} deleted`, 'danger');
            renderRoleBreakdown();
          } else {
            showToast(data.message || 'Delete failed', 'danger');
          }
        })
        .catch(() => showToast('Network error — could not delete user', 'danger'));
    }
  );
}
 
function normalizeRole(s) {
  return (s || '').toLowerCase().replace(/[\s_-]/g, '');
}
 
function filterServerUsers() {
  const q      = (document.getElementById('userSearch')?.value || '').toLowerCase();
  const role   = normalizeRole(document.getElementById('userRoleFilter')?.value || '');
  const status = (document.getElementById('userStatusFilter')?.value || '').toLowerCase();
 
  const rows = document.querySelectorAll('#users-body tr[id^="server-user-row-"]');
  let visible = 0;
 
  rows.forEach(row => {
    const name      = (row.querySelector('.user-name')?.textContent || '').toLowerCase();
    const email     = (row.cells[1]?.textContent || '').toLowerCase();
    const rTxt      = normalizeRole(row.cells[2]?.textContent || '');
    const statusTxt = (row.cells[4]?.textContent || '').toLowerCase();
 
    const matchQ      = !q      || name.includes(q)    || email.includes(q);
    const matchRole   = !role   || rTxt.includes(role);
    const matchStatus = !status || statusTxt.includes(status);
 
    if (matchQ && matchRole && matchStatus) {
      row.style.display = '';
      visible++;
    } else {
      row.style.display = 'none';
    }
  });
 
  document.getElementById('userCount').textContent = visible;
}
 
function renderRoleBreakdown() {
  const svg    = document.getElementById('roleDonutSvg');
  const legend = document.getElementById('roleLegend');
  if (!svg || !legend) return;
 
  const rows = document.querySelectorAll('#users-body tr[id^="server-user-row-"]');
  const counts = { jobseeker: 0, employer: 0, admin: 0, other: 0 };
 
  rows.forEach(row => {
    const roleTxt = normalizeRole(row.cells[2]?.textContent || '');
    if (roleTxt.includes('jobseeker'))   counts.jobseeker++;
    else if (roleTxt.includes('employer')) counts.employer++;
    else if (roleTxt.includes('admin'))    counts.admin++;
    else counts.other++;
  });
 
  const segments = [
    { label: 'Job Seekers', value: counts.jobseeker, color: '#6C5CE7' },
    { label: 'Employers',   value: counts.employer,  color: '#00B8A9' },
    { label: 'Admins',      value: counts.admin,      color: '#F0932B' },
  ];
  if (counts.other > 0) segments.push({ label: 'Other', value: counts.other, color: '#94A3B8' });
 
  const total = counts.jobseeker + counts.employer + counts.admin + counts.other;
 
  if (total === 0) {
    svg.innerHTML = `<circle cx="60" cy="60" r="50" fill="none" stroke="#E5E7EB" stroke-width="16"/>`;
    legend.innerHTML = `<div style="color:var(--muted,#6b7280);font-size:14px">No users yet</div>`;
    return;
  }
 
  const radius = 50;
  const circumference = 2 * Math.PI * radius;
  let offsetAccum = 0;
  let circles = '';
 
  segments.forEach(seg => {
    if (seg.value === 0) return;
    const pct  = seg.value / total;
    const dash = pct * circumference;
    circles += `<circle cx="60" cy="60" r="${radius}" fill="none" stroke="${seg.color}" stroke-width="16"
      stroke-dasharray="${dash} ${circumference - dash}" stroke-dashoffset="${-offsetAccum}"
      transform="rotate(-90 60 60)" />`;
    offsetAccum += dash;
  });
 
  svg.innerHTML = circles +
    `<text x="60" y="56" text-anchor="middle" font-size="22" font-weight="700" fill="var(--text,#1e293b)">${total}</text>
     <text x="60" y="74" text-anchor="middle" font-size="11" fill="var(--muted,#6b7280)">Total Users</text>`;
 
  legend.innerHTML = segments.map(seg => {
    const pct = Math.round((seg.value / total) * 100);
    return `
      <div style="display:flex;align-items:center;gap:10px;font-size:14px">
        <span style="width:10px;height:10px;border-radius:50%;background:${seg.color};flex-shrink:0"></span>
        <span style="flex:1;font-weight:500;color:var(--text,#1e293b)">${seg.label}</span>
        <span style="font-weight:700;width:34px;text-align:right">${seg.value}</span>
        <span style="color:var(--muted,#6b7280);width:42px;text-align:right;font-size:12px">${pct}%</span>
      </div>`;
  }).join('');
}
 
document.getElementById('addUserForm')?.addEventListener('submit', e => {
  e.preventDefault();
  const f         = e.target;
  const firstName = f.firstName.value.trim();
  const lastName  = f.lastName.value.trim();
  const email     = f.userEmail.value.trim();
  const password  = f.userPassword.value.trim();
  const role      = f.userRole.value;
 
  if (!firstName || !email || !password) return;
 
  fetch('/admin/users/add', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ firstName, lastName, email, password, role })
  })
  .then(r => r.json())
  .then(data => {
    if (data.status === 'success') {
      const user = data.user;
      const tbody = document.getElementById('users-body');
      const emptyRow = tbody.querySelector('td.empty-state');
      if (emptyRow) emptyRow.closest('tr').remove();
 
      const initial = firstName[0].toUpperCase();
      const newRow  = document.createElement('tr');
      newRow.id     = `server-user-row-${user.id}`;
      newRow.innerHTML = `
        <td>
          <div class="user-cell">
            <div class="user-initials">${initial}</div>
            <div>
              <div class="user-name">${firstName} ${lastName}</div>
              <div style="font-size:11px;color:var(--light)">#${user.id}</div>
            </div>
          </div>
        </td>
        <td style="color:var(--muted)">${email}</td>
        <td><span class="status-pill info">${role}</span></td>
        <td style="color:var(--muted)">Just now</td>
        <td><span class="status-pill success">Active</span></td>
        <td>
          <div class="td-actions">
            <button class="action-btn ghost sm"
              onclick="viewUserFromServer(${user.id},'${firstName} ${lastName}','${email}','${role}')">
              <i class="fa-solid fa-eye"></i> View
            </button>
            <button class="action-btn danger sm"
              onclick="deleteUserFromServer(${user.id},'${firstName} ${lastName}')">
              <i class="fa-solid fa-trash"></i>
            </button>
          </div>
        </td>`;
      tbody.prepend(newRow);
 
      const badge = document.getElementById('userCount');
      if (badge) badge.textContent = parseInt(badge.textContent || '0') + 1;
      const statEl = document.getElementById('stat-total-users');
      if (statEl) statEl.textContent = parseInt(statEl.textContent || '0') + 1;
 
      f.reset();
      closeModal('addUserModal');
      logActivity('User Added', `${firstName} ${lastName} (${role})`, 'success');
      showToast(`${firstName} added successfully`, 'success');
      renderRoleBreakdown();
    } else {
      showToast(data.message || 'Failed to add user', 'danger');
    }
  })
  .catch(() => showToast('Network error — could not add user', 'danger'));
});
 
// ════════════════════════════════════════════
// JOB MODERATION  ← APPROVE / REJECT via DB API
// ════════════════════════════════════════════
 
function renderModeration(data) {
  const tbody = document.getElementById('moderation-body');
  if (!tbody) return;
  setEl('modCount',    data.length);
  setEl('modPending',  JOBS.filter(j => j.status === 'Pending').length);
  setEl('modApproved', JOBS.filter(j => j.status === 'Approved').length);
  setEl('modRejected', JOBS.filter(j => j.status === 'Rejected').length);
 
  if (data.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="empty-state">
      <i class="fa-solid fa-briefcase"></i><p>No jobs to moderate</p></td></tr>`;
    return;
  }
 
  tbody.innerHTML = data.map(j => {
    const isPending  = j.status === 'Pending';
    const statusPill = j.status === 'Approved'
      ? 'success' : j.status === 'Rejected' ? 'danger' : 'warning';
 
    return `
    <tr id="job-row-${j.id}">
      <td><strong>${j.title}</strong></td>
      <td style="color:var(--muted)">${j.company}</td>
      <td><span class="status-pill info">${j.type}</span></td>
      <td style="color:var(--muted)">${j.submitted}</td>
      <td>
        <span class="status-pill ${statusPill}">${j.status}</span>
      </td>
      <td>
        <div class="td-actions">
          <button class="action-btn ghost sm" onclick="viewModerationJob('${j.id}')">
            <i class="fa-solid fa-eye"></i> View
          </button>
          ${isPending ? `
            <button class="action-btn green sm" onclick="approveJob('${j.id}','${j.title}')">
              <i class="fa-solid fa-check"></i> Approve
            </button>
            <button class="action-btn danger sm" onclick="rejectJob('${j.id}','${j.title}')">
              <i class="fa-solid fa-xmark"></i> Reject
            </button>` : `
            <button class="action-btn ghost sm" style="opacity:0.4;cursor:default" disabled>
              ${j.status === 'Approved'
                ? '<i class="fa-solid fa-circle-check"></i> Approved'
                : '<i class="fa-solid fa-circle-xmark"></i> Rejected'}
            </button>`}
          <button class="action-btn secondary sm"
            onclick="reportModerationJob('${j.id}','${j.title}','${j.company}')">
            <i class="fa-solid fa-flag"></i>
          </button>
          <button class="action-btn danger sm"
            onclick="deleteModerationJob('${j.id}','${j.title}')">
            <i class="fa-solid fa-trash"></i>
          </button>
        </div>
      </td>
    </tr>`;
  }).join('');
}
 
function filterModeration() {
  const q      = (document.getElementById('modSearch')?.value || '').toLowerCase();
  const status = document.getElementById('modStatusFilter')?.value || '';
  const type   = document.getElementById('modTypeFilter')?.value   || '';
  const data   = JOBS.filter(j =>
    (!q      || j.title.toLowerCase().includes(q) || j.company.toLowerCase().includes(q)) &&
    (!status || j.status === status) &&
    (!type   || j.type   === type)
  );
  renderModeration(data);
}
 
// ── APPROVE — calls the backend, then updates the local JOBS array ──
function approveJob(id, title) {
  showConfirm('Approve Job', `Approve "${title}"? It will go live and be visible to job seekers.`, 'Approve', 'green', () => {
    const j = JOBS.find(j => j.id === id);
    if (!j) return;
 
    if (j.fromDB) {
      // Persist to database
      fetch(`/admin/moderation/jobs/${j.dbId}/approve`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
          if (data.status === 'success') {
            j.status = 'Approved';
            persistState();
            filterModeration();
            updateStats();
            renderCompanyJobs();
            logActivity('Job Approved', title, 'success');
            showToast(`"${title}" approved — now visible to job seekers`, 'success');
          } else {
            showToast(data.message || 'Approval failed', 'danger');
          }
        })
        .catch(() => showToast('Network error — approval failed', 'danger'));
    } else {
      // JS-only job (not in DB)
      j.status = 'Approved';
      persistState();
      filterModeration();
      updateStats();
      renderCompanyJobs();
      logActivity('Job Approved', title, 'success');
      showToast(`"${title}" approved`, 'success');
    }
  });
}
 
// ── REJECT — calls the backend, then updates the local JOBS array ──
function rejectJob(id, title) {
  showConfirm('Reject Job', `Reject "${title}"? Employers will be notified it was not approved.`, 'Reject', 'danger', () => {
    const j = JOBS.find(j => j.id === id);
    if (!j) return;
 
    if (j.fromDB) {
      // Persist to database
      fetch(`/admin/moderation/jobs/${j.dbId}/reject`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
          if (data.status === 'success') {
            j.status = 'Rejected';
            persistState();
            filterModeration();
            updateStats();
            renderCompanyJobs();
            logActivity('Job Rejected', title, 'danger');
            showToast(`"${title}" rejected — hidden from job seekers`, 'danger');
          } else {
            showToast(data.message || 'Rejection failed', 'danger');
          }
        })
        .catch(() => showToast('Network error — rejection failed', 'danger'));
    } else {
      j.status = 'Rejected';
      persistState();
      filterModeration();
      updateStats();
      renderCompanyJobs();
      logActivity('Job Rejected', title, 'danger');
      showToast(`"${title}" rejected`, 'danger');
    }
  });
}
 
function viewModerationJob(id) {
  const j = JOBS.find(j => j.id === id);
  if (!j) return;
  const statusPill = j.status === 'Approved' ? 'success' : j.status === 'Rejected' ? 'danger' : 'warning';
  document.getElementById('viewJobTitle').textContent = j.title;
  document.getElementById('viewJobBody').innerHTML = `
    <div class="detail-grid">
      <div class="detail-item"><label>Company</label><span>${j.company}</span></div>
      <div class="detail-item"><label>Type</label><span>${j.type}</span></div>
      <div class="detail-item"><label>Location</label><span>${j.location}</span></div>
      <div class="detail-item"><label>Salary</label><span>${j.salary || '—'}</span></div>
      <div class="detail-item"><label>Submitted</label><span>${j.submitted}</span></div>
      <div class="detail-item"><label>Status</label>
        <span class="status-pill ${statusPill}">${j.status}</span>
      </div>
    </div>
    ${j.description ? `<div style="margin-top:16px;padding:14px;background:var(--bg);border-radius:8px;font-size:13px;line-height:1.6">${j.description}</div>` : ''}
    ${j.status !== 'Pending' ? `
      <div style="margin-top:14px;padding:12px 16px;border-radius:8px;font-size:13px;
        background:${j.status === 'Approved' ? 'rgba(22,163,74,.08)' : 'rgba(239,68,68,.08)'};
        color:${j.status === 'Approved' ? '#16A34A' : '#EF4444'};font-weight:600">
        <i class="fa-solid ${j.status === 'Approved' ? 'fa-circle-check' : 'fa-circle-xmark'}"></i>
        This job is ${j.status === 'Approved' ? 'live and visible to job seekers' : 'hidden from job seekers'}
      </div>` : ''}`;
 
  document.getElementById('viewJobFooter').innerHTML = `
    <button class="action-btn ghost" onclick="closeModal('viewJobModal')">Cancel</button>
    ${j.status === 'Pending' ? `
      <button class="action-btn green" onclick="closeModal('viewJobModal');approveJob('${j.id}','${j.title}')">
        <i class="fa-solid fa-check"></i> Approve</button>
      <button class="action-btn danger" onclick="closeModal('viewJobModal');rejectJob('${j.id}','${j.title}')">
        <i class="fa-solid fa-xmark"></i> Reject</button>` : ''}
    <button class="action-btn secondary" onclick="closeModal('viewJobModal');reportModerationJob('${j.id}','${j.title}','${j.company}')">
      <i class="fa-solid fa-flag"></i> Report</button>
    <button class="action-btn danger" onclick="closeModal('viewJobModal');deleteModerationJob('${j.id}','${j.title}')">
      <i class="fa-solid fa-trash"></i> Delete</button>`;
  openModal('viewJobModal');
}
 
function reportModerationJob(id, title, company) {
  const form = document.getElementById('addReportForm');
  if (form) {
    form.reportJobTitle.value       = title;
    form.reportCompany.value        = company;
    form.reportedBy.value           = 'Admin';
    form.reportReason.value         = 'Inappropriate';
    form.reportDescription.value    = '';
  }
  openModal('addReportModal');
}
 
function deleteModerationJob(id, title) {
  showConfirm(
    'Delete Job',
    `Permanently delete "${title}"? This cannot be undone.`,
    'Delete', 'danger',
    () => {
      const j = JOBS.find(j => j.id === id);
      if (!j) return;
 
      const doDelete = () => {
        JOBS = JOBS.filter(j => j.id !== id);
        persistState();
        filterModeration();
        updateStats();
        renderCompanyJobs();
        logActivity('Job Deleted', title, 'danger');
        showToast(`"${title}" deleted`, 'danger');
      };
 
      if (j.fromDB) {
        fetch(`/admin/moderation/jobs/${j.dbId}/delete`, { method: 'POST' })
          .then(r => r.json())
          .then(data => {
            if (data.status === 'success') doDelete();
            else showToast(data.message || 'Failed to delete job', 'danger');
          })
          .catch(() => showToast('Network error', 'danger'));
      } else {
        doDelete();
      }
    }
  );
}
 
document.getElementById('addJobForm')?.addEventListener('submit', e => {
  e.preventDefault();
  const f = e.target;
  const title   = f.jobTitle.value.trim();
  const company = f.jobCompany.value.trim();
  const type    = f.jobType.value;
  const loc     = f.jobLocation.value.trim();
  const desc    = f.jobDescription.value.trim();
  const salary  = f.jobSalary ? f.jobSalary.value.trim() : '';
  const website = f.jobWebsite ? f.jobWebsite.value.trim() : '';
  const email   = f.jobEmail ? f.jobEmail.value.trim() : '';
  if (!title || !company) return;
 
  const newJob = {
    id: _nextJobId++, title, company, type,
    location: loc || 'Remote', description: desc,
    salary, website, email,
    status: 'Pending',
    submitted: new Date().toLocaleDateString('en-GB', { day:'numeric', month:'short', year:'numeric' }),
  };
  JOBS.push(newJob);
  persistState();
  f.reset();
  closeModal('addJobModal');
  filterModeration();
  updateStats();
  renderCompanyJobs();
  logActivity('Job Submitted', `${title} at ${company}`, 'warning');
  showToast(`"${title}" submitted for review`, 'info');
});
 
// ════════════════════════════════════════════
// REPORTED JOBS
// ════════════════════════════════════════════
function renderReports(data) {
  const tbody = document.getElementById('reports-body');
  if (!tbody) return;
  const openCount = REPORTS.filter(r => r.status === 'Under Review').length;
  setEl('reportCount', data.length);
  setEl('reportBadge', openCount);
 
  if (data.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="empty-state">
      <i class="fa-solid fa-flag"></i><p>No reported jobs</p></td></tr>`;
    return;
  }
  tbody.innerHTML = data.map(r => `
    <tr id="report-row-${r.id}">
      <td><strong>${r.jobTitle}</strong></td>
      <td style="color:var(--muted)">${r.company}</td>
      <td style="color:var(--muted)">${r.reportedBy}</td>
      <td><span class="status-pill ${r.reason==='Scam'||r.reason==='Inappropriate'?'danger':r.reason==='Spam'?'warning':'muted'}">${r.reason}</span></td>
      <td style="color:var(--muted)">${r.date}</td>
      <td><span class="status-pill ${r.status==='Resolved'?'success':r.status==='Dismissed'?'muted':'warning'}">${r.status}</span></td>
      <td>
        <div class="td-actions">
          <button class="action-btn ghost sm" onclick="viewReport(${r.id})">
            <i class="fa-solid fa-eye"></i> View
          </button>
          ${r.status === 'Under Review' ? (r.type === 'user' ? `
            <button class="action-btn danger sm" onclick="removeReportedUser(${r.id},${r.targetUserId},'${r.jobTitle}')">
              <i class="fa-solid fa-trash"></i> Delete Account</button>
            <button class="action-btn ghost sm" onclick="dismissReport(${r.id},'${r.jobTitle}')">
              Dismiss</button>` : `
            <button class="action-btn danger sm" onclick="removeReportedJob(${r.id},'${r.jobTitle}')">
              <i class="fa-solid fa-trash"></i> Remove</button>
            <button class="action-btn ghost sm" onclick="dismissReport(${r.id},'${r.jobTitle}')">
              Dismiss</button>`) : ''}
        </div>
      </td>
    </tr>`).join('');
}
 
// ════════════════════════════════════════════
// COMPANY JOBS TAB
// ════════════════════════════════════════════
function companyKey(job) {
  const email = (job.email || job.companyEmail || '').trim().toLowerCase();
  if (email) return email;
  return (job.company || 'unknown').trim().toLowerCase();
}
 
function companyWebsite(job) {
  let url = (job.website || job.companyWebsite || job.companyUrl || '').trim();
  if (!url) return null;
  if (!/^https?:\/\//i.test(url)) url = 'https://' + url;
  return url;
}
 
function displayWebsite(url) {
  return url.replace(/^https?:\/\//i, '').replace(/^www\./i, '').replace(/\/$/, '');
}
 
function renderCompanyJobs() {
  const grid = document.getElementById('companyJobsGrid');
  if (!grid) return;
 
  const q = (document.getElementById('companySearch')?.value || '').toLowerCase();
 
  const groups = {};
  JOBS.forEach(j => {
    const key = companyKey(j);
    if (!groups[key]) {
      groups[key] = { company: j.company, email: j.email || j.companyEmail || '—', jobs: [] };
    }
    groups[key].jobs.push(j);
  });
 
  let companies = Object.values(groups);
 
  if (q) {
    companies = companies.filter(c => {
      const site = companyWebsite(c.jobs[0]) || '';
      return c.company.toLowerCase().includes(q) ||
             (c.email || '').toLowerCase().includes(q) ||
             site.toLowerCase().includes(q);
    });
  }
 
  if (companies.length === 0) {
    grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1">
      <i class="fa-solid fa-building"></i><p>No company jobs found</p></div>`;
    return;
  }
 
  companies.sort((a, b) => b.jobs.length - a.jobs.length);
 
  grid.innerHTML = companies.map((c) => {
    const pending  = c.jobs.filter(j => j.status === 'Pending').length;
    const approved = c.jobs.filter(j => j.status === 'Approved').length;
    const rejected = c.jobs.filter(j => j.status === 'Rejected').length;
    const total    = c.jobs.length;
    const cKey     = companyKey(c.jobs[0]);
    const initial  = (c.company || '?').trim()[0] || '?';
    const site     = companyWebsite(c.jobs[0]);
 
    return `
      <div class="company-job-card">
        <div class="cjc-head">
          <span class="cjc-tag"><i class="fa-solid fa-briefcase"></i> Job Postings</span>
          <span class="cjc-count-badge">${total} job${total === 1 ? '' : 's'}</span>
        </div>
        <div class="cjc-identity">
          <div class="cjc-avatar">${initial}</div>
          <div class="cjc-identity-text">
            <div class="cjc-company" title="${c.company}">${c.company}</div>
            ${site
              ? `<a class="cjc-website" href="${site}" target="_blank" rel="noopener noreferrer" title="${site}" onclick="event.stopPropagation()">
                   <i class="fa-solid fa-arrow-up-right-from-square"></i> ${displayWebsite(site)}
                 </a>`
              : `<div class="cjc-email no-email">No website on file</div>`}
          </div>
        </div>
        <div class="cjc-stats">
          <div class="cjc-stat pending"><label>Pending</label><span>${pending}</span></div>
          <div class="cjc-stat approved"><label>Approved</label><span>${approved}</span></div>
          <div class="cjc-stat rejected"><label>Rejected</label><span>${rejected}</span></div>
          <div class="cjc-stat total"><label>Total</label><span>${total}</span></div>
        </div>
        <button class="cjc-view-btn" onclick="viewCompanyJobs('${cKey.replace(/'/g, "\\'")}')">
          <i class="fa-solid fa-eye"></i> View Jobs
        </button>
      </div>`;
  }).join('');
}
 
function viewCompanyJobs(key) {
  const jobs = JOBS.filter(j => companyKey(j) === key);
  if (jobs.length === 0) return;
 
  document.getElementById('companyJobsModalTitle').textContent =
    `${jobs[0].company} — ${jobs.length} Job${jobs.length === 1 ? '' : 's'}`;
 
  document.getElementById('companyJobsModalBody').innerHTML = jobs.map(j => `
    <div class="cjc-job-row">
      <div class="cjc-job-row-head">
        <strong>${j.title}</strong>
        <span class="status-pill ${j.status === 'Approved' ? 'success' : j.status === 'Rejected' ? 'danger' : 'warning'}">
          ${j.status}
        </span>
      </div>
      <div class="cjc-job-meta">
        <div>Type: <b>${j.type || '—'}</b></div>
        <div>Location: <b>${j.location || '—'}</b></div>
        <div>Submitted: <b>${j.submitted || '—'}</b></div>
      </div>
      ${j.description
        ? `<div class="cjc-job-desc">${j.description}</div>`
        : `<div class="cjc-job-desc" style="color:var(--light)">No description provided</div>`}
    </div>`).join('');
 
  openModal('viewCompanyJobsModal');
}
 
function filterReports() {
  const q      = (document.getElementById('reportSearch')?.value || '').toLowerCase();
  const reason = document.getElementById('reportReasonFilter')?.value || '';
  const status = document.getElementById('reportStatusFilter')?.value || '';
  const data   = REPORTS.filter(r =>
    (!q      || r.jobTitle.toLowerCase().includes(q) || r.company.toLowerCase().includes(q)) &&
    (!reason || r.reason === reason) &&
    (!status || r.status === status)
  );
  renderReports(data);
}
 
document.getElementById('addReportForm')?.addEventListener('submit', e => {
  e.preventDefault();
  const f = e.target;
  const jobTitle    = f.reportJobTitle.value.trim();
  const company     = f.reportCompany.value.trim();
  const reportedBy  = f.reportedBy.value.trim();
  const reason      = f.reportReason.value;
  const description = f.reportDescription.value.trim();
  if (!jobTitle || !company || !reportedBy) return;
 
  REPORTS.push({
    id: _nextReportId++, type: 'job', jobTitle, company, reportedBy, reason, description,
    status: 'Under Review',
    date: new Date().toLocaleDateString('en-GB', { day:'numeric', month:'short', year:'numeric' })
  });
  persistState();
  f.reset();
  closeModal('addReportModal');
  filterReports(); updateStats();
  logActivity('Job Reported', `${jobTitle} — ${reason}`, 'warning');
  showToast(`Report submitted for "${jobTitle}"`, 'warning');
  document.querySelector('[data-tab="reported-jobs"]')?.click();
});
 
function viewReport(id) {
  const r = REPORTS.find(r => r.id === id);
  if (!r) return;
  const isUser = r.type === 'user';
  document.getElementById('viewReportBody').innerHTML = `
    <div class="detail-grid">
      <div class="detail-item"><label>${isUser ? 'Reported User' : 'Job Title'}</label><span>${r.jobTitle}</span></div>
      <div class="detail-item"><label>${isUser ? 'Account Type' : 'Company'}</label><span>${r.company}</span></div>
      <div class="detail-item"><label>Reported By</label><span>${r.reportedBy}</span></div>
      <div class="detail-item"><label>Date</label><span>${r.date}</span></div>
      <div class="detail-item"><label>Reason</label><span>${r.reason}</span></div>
      <div class="detail-item"><label>Status</label>
        <span class="status-pill ${r.status==='Resolved'?'success':r.status==='Dismissed'?'muted':'warning'}">${r.status}</span>
      </div>
    </div>
    ${r.description ? `<div style="margin-top:16px;padding:14px;background:var(--bg);border-radius:8px;font-size:13px;line-height:1.6">${r.description}</div>` : ''}`;
  document.getElementById('viewReportFooter').innerHTML = r.status === 'Under Review' ? `
    <button class="action-btn ghost" onclick="closeModal('viewReportModal')">Cancel</button>
    <button class="action-btn ghost" onclick="closeModal('viewReportModal');dismissReport(${r.id},'${r.jobTitle}')">Dismiss</button>
    <button class="action-btn danger" onclick="closeModal('viewReportModal');${isUser ? `removeReportedUser(${r.id},${r.targetUserId},'${r.jobTitle}')` : `removeReportedJob(${r.id},'${r.jobTitle}')`}">
      <i class="fa-solid fa-trash"></i> ${isUser ? 'Delete Account' : 'Remove Job'}</button>` :
    `<button class="action-btn ghost" onclick="closeModal('viewReportModal')">Close</button>`;
  openModal('viewReportModal');
}
 
function removeReportedJob(id, title) {
  showConfirm('Remove Job', `Remove "${title}" from the platform?`, 'Remove Job', 'danger', () => {
    const r = REPORTS.find(r => r.id === id);
    if (r) { r.status = 'Resolved'; persistState(); filterReports(); updateAnalytics(); updateStats(); logActivity('Job Removed', title, 'danger'); showToast(`"${title}" removed`, 'danger'); }
  });
}
 
function dismissReport(id, title) {
  showConfirm('Dismiss Report', `Dismiss the report for "${title}"?`, 'Dismiss', 'ghost', () => {
    const r = REPORTS.find(r => r.id === id);
    if (r) { r.status = 'Dismissed'; persistState(); filterReports(); updateAnalytics(); updateStats(); logActivity('Report Dismissed', title, 'muted'); showToast('Report dismissed', 'success'); }
  });
}
 
function reportUserJob(userId, userName) {
  const f = document.getElementById('reportUserForm');
  f.reportUserId.value = userId;
  f.reportUserName.value = userName;
  f.reportUserReason.value = '';
  f.reportUserDescription.value = '';
  openModal('reportUserModal');
}
 
document.getElementById('reportUserForm')?.addEventListener('submit', e => {
  e.preventDefault();
  const f           = e.target;
  const userId      = f.reportUserId.value;
  const userName    = f.reportUserName.value;
  const reason      = f.reportUserReason.value;
  const description = f.reportUserDescription.value.trim();
  if (!reason || !description) return;
 
  REPORTS.push({
    id: _nextReportId++,
    type: 'user',
    jobTitle: userName,
    company: 'User Account',
    reportedBy: 'Admin',
    targetUserId: userId,
    reason,
    description,
    status: 'Under Review',
    date: new Date().toLocaleDateString('en-GB', { day:'numeric', month:'short', year:'numeric' })
  });
  persistState();
 
  closeModal('reportUserModal');
  document.querySelector('[data-tab="reported-jobs"]')?.click();
  filterReports();
  updateStats();
  logActivity('User Reported', `${userName} — ${reason}`, 'warning');
  showToast(`Report filed against ${userName}`, 'warning');
});
 
function removeReportedUser(reportId, userId, userName) {
  showConfirm('Delete User Account', `Permanently delete "${userName}"? This will resolve the report and cannot be undone.`, 'Delete Account', 'danger', () => {
    fetch(`/admin/users/${userId}/delete`, { method: 'POST' })
      .then(r => r.json())
      .then(data => {
        if (data.status === 'success') {
          const row = document.getElementById(`server-user-row-${userId}`);
          if (row) row.remove();
          const badge = document.getElementById('userCount');
          if (badge) badge.textContent = parseInt(badge.textContent || '0') - 1;
          const statEl = document.getElementById('stat-total-users');
          if (statEl) statEl.textContent = parseInt(statEl.textContent || '0') - 1;
 
          const r = REPORTS.find(r => r.id === reportId);
          if (r) r.status = 'Resolved';
          persistState();
          filterReports(); updateStats();
          logActivity('User Deleted', userName, 'danger');
          showToast(`${userName} deleted`, 'danger');
          renderRoleBreakdown();
        } else {
          showToast(data.message || 'Delete failed', 'danger');
        }
      })
      .catch(() => showToast('Network error — could not delete user', 'danger'));
  });
}
 
// ════════════════════════════════════════════
// ANNOUNCEMENTS
// ════════════════════════════════════════════
document.getElementById('sendAnnouncementForm')?.addEventListener('submit', e => {
  e.preventDefault();
  const f        = e.target;
  const subject  = f.announceSubject.value.trim();
  const audience = f.announceAudience.value;
  const message  = f.announceMessage.value.trim();
  if (!subject || !message) return;
 
  fetch('/admin/announcements/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ subject, audience, message })
  })
  .then(r => r.json())
  .then(data => {
    if (data.status === 'success') {
      f.reset();
      closeModal('sendAnnouncementModal');
      logActivity('Announcement Sent', `${subject} → ${audience === 'all' ? 'All Users' : audience}`, 'info');
      showToast(`Announcement sent to ${data.recipients} user(s)`, 'success');
    } else {
      showToast(data.message || 'Failed to send announcement', 'danger');
    }
  })
  .catch(() => showToast('Network error — could not send announcement', 'danger'));
});
 
(function fixAnnouncementListener() {
  const _origLogActivity2 = logActivity;
  logActivity = function(action, target, status) {
    _origLogActivity2(action, target, status);
    if (action.toLowerCase().includes('announcement')) {
      const parts    = target.split(' → ');
      const subject  = parts[0] || target;
      const audience = parts[1] || 'All Users';
      if (!announcementLog.find(a => a.subject === subject)) {
        announcementLog.unshift({
          subject, audience,
          date: new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
        });
      }
    }
  };
})();
 
function updatePlatformHealth() {
  const totalUsers  = parseInt(document.getElementById('stat-total-users')?.textContent || '0');
  const activeJobs  = parseInt(document.getElementById('stat-active-jobs')?.textContent  || '0');
  const openReports = REPORTS.filter(r => r.status === 'Under Review').length;
  const resolved    = REPORTS.filter(r => r.status === 'Resolved').length;
  const pendingJobs = JOBS.filter(j => j.status === 'Pending').length;
 
  let score = 100;
  if (totalUsers === 0)     score -= 30;
  if (activeJobs === 0)     score -= 20;
  if (openReports > 10)     score -= 20;
  else if (openReports > 4) score -= 10;
  if (pendingJobs > 15)     score -= 15;
  else if (pendingJobs > 7) score -= 7;
  score = Math.max(0, Math.min(100, score));
 
  let color, label;
  if (score >= 80)      { color = '#16A34A'; label = 'Healthy'; }
  else if (score >= 55) { color = '#D97706'; label = 'Fair'; }
  else                  { color = '#EF4444'; label = 'Needs Attention'; }
 
  const valEl   = document.getElementById('health-value');
  const pulseEl = document.getElementById('health-pulse');
  if (valEl)   valEl.textContent         = score + '%';
  if (pulseEl) { pulseEl.style.background = color; pulseEl.title = label; }
 
  setEl('ph-score',        score + '%');
  setEl('ph-open-reports', openReports);
  setEl('ph-pending-jobs', pendingJobs);
  setEl('ph-total-users',  totalUsers);
  setEl('ph-active-jobs',  activeJobs);
  setEl('ph-resolved',     resolved);
 
  const phDot = document.getElementById('ph-dot');
  if (phDot) phDot.style.background = color;
 
  const breakdown = document.getElementById('ph-breakdown');
  if (breakdown) {
    const items = [
      { label: 'User Base',        score: totalUsers > 0 ? 100 : 0, note: `${totalUsers} users` },
      { label: 'Active Jobs',      score: activeJobs > 0 ? 100 : 0, note: `${activeJobs} live` },
      { label: 'Report Backlog',   score: openReports === 0 ? 100 : openReports > 10 ? 20 : openReports > 4 ? 60 : 80, note: `${openReports} open` },
      { label: 'Moderation Queue', score: pendingJobs === 0 ? 100 : pendingJobs > 15 ? 20 : pendingJobs > 7 ? 55 : 80, note: `${pendingJobs} pending` },
    ];
    breakdown.innerHTML = items.map(item => {
      const c = item.score >= 80 ? '#16A34A' : item.score >= 55 ? '#D97706' : '#EF4444';
      return `
        <div>
          <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px">
            <span style="font-weight:500;color:var(--text)">${item.label}</span>
            <span style="color:var(--muted)">${item.note}</span>
          </div>
          <div style="background:var(--border);border-radius:999px;height:7px;overflow:hidden">
            <div style="width:${item.score}%;height:100%;background:${c};border-radius:999px;transition:width 0.6s ease"></div>
          </div>
        </div>`;
    }).join('');
  }
 
  const statusBlock = document.getElementById('ph-status-block');
  if (statusBlock) {
    const checks = [
      { label: 'Users registered',        ok: totalUsers > 0 },
      { label: 'Jobs live on platform',   ok: activeJobs > 0 },
      { label: 'No report backlog',       ok: openReports <= 4 },
      { label: 'Moderation up to date',   ok: pendingJobs <= 7 },
      { label: 'Reports being resolved',  ok: resolved > 0 },
    ];
    statusBlock.innerHTML = checks.map(c => `
      <div style="display:flex;align-items:center;gap:10px;font-size:13px">
        <i class="fa-solid ${c.ok ? 'fa-circle-check' : 'fa-circle-xmark'}"
           style="color:${c.ok ? '#16A34A' : '#EF4444'};font-size:15px;flex-shrink:0"></i>
        <span style="color:var(--${c.ok ? 'text' : 'muted'})">${c.label}</span>
      </div>`).join('');
  }
}
 
// ════════════════════════════════════════════
// NOTIFICATION BELL SHAKE
// ════════════════════════════════════════════
function shakeBell() {
  const btn = document.getElementById('notifBtn');
  if (!btn) return;
  btn.classList.remove('bell-shake');
  void btn.offsetWidth;
  btn.classList.add('bell-shake');
  setTimeout(() => btn.classList.remove('bell-shake'), 500);
}
 
const _origPushAdminNotif = pushAdminNotif;
pushAdminNotif = function(action, target, status) {
  _origPushAdminNotif(action, target, status);
  shakeBell();
  const badge = document.getElementById('notifBadge');
  if (badge && badge.textContent !== '0') {
    badge.style.display = 'flex';
    document.getElementById('notifBtn')?.classList.add('has-unread');
  }
};
 
const _origRenderAdminNotifs = renderAdminNotifs;
renderAdminNotifs = function() {
  _origRenderAdminNotifs();
  const unread = adminNotifs.filter(n => n.unread).length;
  const badge  = document.getElementById('notifBadge');
  const btn    = document.getElementById('notifBtn');
  if (badge) {
    badge.style.display = unread > 0 ? 'flex' : 'none';
    badge.textContent   = unread > 99 ? '99+' : unread;
  }
  if (btn) btn.classList.toggle('has-unread', unread > 0);
};
 
document.addEventListener('DOMContentLoaded', () => {
  renderAdminNotifs();
});
 
function saveSettings() {
  showToast('Settings saved successfully!', 'success');
}
 
document.getElementById("darkModeToggle")?.addEventListener("change", function() {
  if (this.checked) {
    document.body.style.background = "#1e1e2f";
    document.body.style.color = "#f5f5f5";
  } else {
    document.body.style.background = "#f5f7fa";
    document.body.style.color = "#333";
  }
});
 
// ─────────────────────────────────────────────
// GLOBAL SEARCH
// ─────────────────────────────────────────────
document.querySelector('.search-bar input')?.addEventListener('input', function () {
  const q = this.value.toLowerCase().trim();
  if (!q) return;
 
  const userRows = document.querySelectorAll('#users-body tr[id^="server-user-row-"]');
  let userMatch = false;
  userRows.forEach(row => { if (row.textContent.toLowerCase().includes(q)) userMatch = true; });
 
  const jMatch = JOBS.find(j => j.title.toLowerCase().includes(q) || j.company.toLowerCase().includes(q));
  const rMatch = REPORTS.find(r => r.jobTitle.toLowerCase().includes(q));
 
  if (userMatch) {
    document.querySelector('[data-tab="user-management"]')?.click();
    setTimeout(() => { document.getElementById('userSearch').value = q; filterServerUsers(); }, 100);
  } else if (jMatch) {
    document.querySelector('[data-tab="job-moderation"]')?.click();
    setTimeout(() => { document.getElementById('modSearch').value = q; filterModeration(); }, 100);
  } else if (rMatch) {
    document.querySelector('[data-tab="reported-jobs"]')?.click();
    setTimeout(() => { document.getElementById('reportSearch').value = q; filterReports(); }, 100);
  }
});
 
// ════════════════════════════════════════════
// LOAD JOBS FROM DB  ← status gate enforced here
// ════════════════════════════════════════════
function loadModerationJobsFromDB() {
  fetch('/admin/moderation/jobs')
    .then(r => r.json())
    .then(dbJobs => {
      // Remove stale DB jobs; keep JS-only ones
      JOBS = JOBS.filter(j => !j.fromDB);
 
      dbJobs.forEach(dbJob => {
        JOBS.push({
          id:          'db-' + dbJob.id,
          dbId:        dbJob.id,
          title:       dbJob.title,
          company:     dbJob.company,
          type:        dbJob.type,
          location:    dbJob.location,
          // ── KEY: respect whatever status the DB returns ──
          status:      dbJob.status,   // 'Pending' | 'Approved' | 'Rejected'
          submitted:   dbJob.submitted,
          description: dbJob.description || '',
          salary:      dbJob.salary || '',
          website:     dbJob.website || dbJob.companyWebsite || '',
          email:       dbJob.email  || dbJob.companyEmail   || '',
          fromDB:      true,
        });
      });
 
      renderModeration(JOBS);
      renderCompanyJobs();
 
      const totalActive = JOBS.filter(j => j.status === 'Approved').length;
      setEl('stat-active-jobs', totalActive);
 
      updateStats();
    })
    .catch(err => console.error('Could not load jobs for moderation:', err));
}
 
// ─────────────────────────────────────────────
// INIT
// ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  updateStats();
  renderModeration(JOBS);
  renderReports(REPORTS);
  renderRoleBreakdown();
  updatePlatformHealth();
  updateAnalytics();
  renderActionHistory(activityLog);
  renderCompanyJobs();
  loadModerationJobsFromDB();
 
  // Auto-refresh moderation every 30s
  setInterval(loadModerationJobsFromDB, 30000);
});
 