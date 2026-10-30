(() => {
  "use strict";

  const API_BASE = window.CAMPUSLY_API_BASE || "/api";
  const STORE_KEY = "campusly-preview-v1";
  const SESSION_KEY = "campusly-session";
  const today = new Date().toISOString().slice(0, 10);
  const icons = {
    grid: '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/>',
    users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    user: '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    book: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z"/>',
    calendar: '<rect x="3" y="4" width="18" height="17" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    wallet: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 9h18M16 14h.01"/><path d="M5 5V3h14v2"/>',
    chart: '<path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-6 6"/>',
    search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
    bell: '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4"/>',
    plus: '<path d="M12 5v14M5 12h14"/>',
    more: '<circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>',
    eye: '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>',
    edit: '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L8 18l-4 1 1-4Z"/>',
    trash: '<path d="M3 6h18M8 6V4h8v2m3 0-1 14H6L5 6m4 4v6m6-6v6"/>',
    logout: '<path d="M10 17l5-5-5-5M15 12H3"/><path d="M12 3h7a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-7"/>',
    download: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>',
    close: '<path d="m18 6-12 12M6 6l12 12"/>',
    check: '<path d="m5 12 4 4L19 6"/>',
    help: '<circle cx="12" cy="12" r="10"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3m.1 4h.01"/>',
    bookOpen: '<path d="M12 7v14M3 18V5a2 2 0 0 1 2-2h3a4 4 0 0 1 4 4 4 4 0 0 1 4-4h3a2 2 0 0 1 2 2v13a2 2 0 0 1-2 2h-3a4 4 0 0 0-4 2 4 4 0 0 0-4-2H5a2 2 0 0 1-2-2Z"/>'
  };
  const icon = (name, cls = "") => `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${icons[name] || icons.grid}</svg>`;

  const seed = {
    students: [
      { id: "STU-2401", name: "Olivia Rhye", email: "olivia.rhye@campus.edu", phone: "+1 555 013 2041", department: "Computer Science", course: "B.Sc. Computer Science", year: "Year 2", status: "Active", attendance: 96, fee: 18500, paid: 18500, initials: "OR", tone: "purple" },
      { id: "STU-2402", name: "Phoenix Baker", email: "phoenix.baker@campus.edu", phone: "+1 555 013 2042", department: "Business", course: "BBA", year: "Year 3", status: "Active", attendance: 89, fee: 16200, paid: 12200, initials: "PB", tone: "orange" },
      { id: "STU-2403", name: "Lana Steiner", email: "lana.steiner@campus.edu", phone: "+1 555 013 2043", department: "Design", course: "B.Des. Visual Design", year: "Year 1", status: "Active", attendance: 94, fee: 14800, paid: 14800, initials: "LS", tone: "green" },
      { id: "STU-2404", name: "Demi Wilkinson", email: "demi.wilkinson@campus.edu", phone: "+1 555 013 2044", department: "Computer Science", course: "B.Sc. Computer Science", year: "Year 2", status: "Active", attendance: 78, fee: 18500, paid: 10000, initials: "DW", tone: "blue" },
      { id: "STU-2405", name: "Candice Wu", email: "candice.wu@campus.edu", phone: "+1 555 013 2045", department: "Business", course: "BBA", year: "Year 1", status: "Active", attendance: 91, fee: 16200, paid: 16200, initials: "CW", tone: "purple" },
      { id: "STU-2406", name: "Natali Craig", email: "natali.craig@campus.edu", phone: "+1 555 013 2046", department: "Design", course: "B.Des. Visual Design", year: "Year 3", status: "Active", attendance: 86, fee: 14800, paid: 7800, initials: "NC", tone: "orange" }
    ],
    teachers: [
      { id: "TCH-1021", name: "Dr. Alex Morgan", email: "alex.morgan@campus.edu", phone: "+1 555 010 1021", department: "Computer Science", subject: "Data Structures", experience: "8 years", status: "Active", initials: "AM", tone: "purple" },
      { id: "TCH-1022", name: "Sofia Chen", email: "sofia.chen@campus.edu", phone: "+1 555 010 1022", department: "Business", subject: "Business Strategy", experience: "6 years", status: "Active", initials: "SC", tone: "green" },
      { id: "TCH-1023", name: "Ethan Brooks", email: "ethan.brooks@campus.edu", phone: "+1 555 010 1023", department: "Design", subject: "Visual Communication", experience: "5 years", status: "Active", initials: "EB", tone: "orange" },
      { id: "TCH-1024", name: "Maya Patel", email: "maya.patel@campus.edu", phone: "+1 555 010 1024", department: "Computer Science", subject: "Web Development", experience: "4 years", status: "Active", initials: "MP", tone: "blue" }
    ],
    courses: [
      { id: "CRS-101", name: "B.Sc. Computer Science", department: "Computer Science", teacher: "Dr. Alex Morgan", students: 128, capacity: 160, duration: "3 years", status: "Active", symbol: "CS" },
      { id: "CRS-102", name: "BBA", department: "Business", teacher: "Sofia Chen", students: 96, capacity: 120, duration: "3 years", status: "Active", symbol: "BA" },
      { id: "CRS-103", name: "B.Des. Visual Design", department: "Design", teacher: "Ethan Brooks", students: 74, capacity: 100, duration: "4 years", status: "Active", symbol: "VD" },
      { id: "CRS-104", name: "B.Sc. Data Analytics", department: "Computer Science", teacher: "Maya Patel", students: 82, capacity: 100, duration: "3 years", status: "Active", symbol: "DA" },
      { id: "CRS-105", name: "MBA", department: "Business", teacher: "Sofia Chen", students: 65, capacity: 80, duration: "2 years", status: "Active", symbol: "MB" }
    ],
    attendance: {},
    fees: [],
    reports: {
      preview: true,
      monthly: [
        { month: "May", score: 48, average: 30 }, { month: "Jun", score: 62, average: 44 },
        { month: "Jul", score: 57, average: 39 }, { month: "Aug", score: 78, average: 60 },
        { month: "Sep", score: 70, average: 52 }, { month: "Oct", score: 87, average: 69 }
      ],
      attendanceByCourse: [
        { course: "B.Sc. Computer Science", attendance: 94 }, { course: "BBA", attendance: 89 },
        { course: "B.Des. Visual Design", attendance: 92 }, { course: "B.Sc. Data Analytics", attendance: 81 },
        { course: "MBA", attendance: 96 }
      ],
      enrollmentTrends: [
        { month: "May", enrollment: 82, graduates: 31 }, { month: "Jun", enrollment: 104, graduates: 39 },
        { month: "Jul", enrollment: 96, graduates: 36 }, { month: "Aug", enrollment: 121, graduates: 49 },
        { month: "Sep", enrollment: 113, graduates: 46 }, { month: "Oct", enrollment: 146, graduates: 63 }
      ]
    },
    preview: true
  };
  seed.attendance[today] = {};
  seed.students.forEach(s => { seed.attendance[today][s.id] = ({ "STU-2401": "Present", "STU-2402": "Present", "STU-2403": "Late", "STU-2404": "Absent", "STU-2405": "Present", "STU-2406": "Present" })[s.id]; });
  let state = loadPreviewState();
  let session = readSession();
  if (session && !session.token) {
    localStorage.removeItem(SESSION_KEY);
    session = null;
  }
  let currentPage = session ? (session.role === "student" ? "portal" : "dashboard") : "login";
  let searchTerm = "";
  let attendanceDate = today;

  function loadPreviewState() {
    try {
      const saved = JSON.parse(localStorage.getItem(STORE_KEY) || "null");
      if (saved && Array.isArray(saved.students)) return { ...structuredClone(seed), ...saved, preview: true };
    } catch (error) {
      console.warn("Could not load preview data:", error);
    }
    return structuredClone(seed);
  }
  function saveState() {
    try { localStorage.setItem(STORE_KEY, JSON.stringify(state)); }
    catch (error) { notify(`Could not save preview data: ${error.message}`, "error"); }
  }
  function readSession() {
    try { return JSON.parse(localStorage.getItem(SESSION_KEY) || "null"); }
    catch (error) { console.warn("Could not read the saved session:", error); return null; }
  }
  const money = value => new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(Number(value || 0));
  const escapeHtml = value => String(value ?? "").replace(/[&<>"']/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
  const initials = name => String(name || "").split(/\s+/).slice(0, 2).map(part => part[0] || "").join("").toUpperCase();
  const byId = (list, id) => list.find(item => item.id === id);
  const currentStudent = () => state.students.find(student => student.id === session?.studentId) || null;
  const canManage = () => session?.role === "admin";
  function notify(message, type = "success") {
    const region = document.getElementById("toast-region");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;
    region.appendChild(toast);
    window.setTimeout(() => toast.remove(), 4200);
  }
  async function apiRequest(resource, options = {}) {
    const response = await fetch(`${API_BASE}/${resource}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(session?.token ? { Authorization: `Bearer ${session.token}` } : {}),
        ...(options.headers || {})
      }
    });
    const payload = response.status === 204 ? null : await response.json().catch(() => null);
    if (!response.ok) {
      const error = new Error(payload?.message || payload?.error || `Request failed (${response.status})`);
      error.status = response.status;
      throw error;
    }
    return payload;
  }
  async function persistMutation(resource, options, description) {
    try {
      await apiRequest(resource, options);
      state.preview = false;
      state.dashboard = null;
      return "api";
    } catch (error) {
      if (!error.status || error.status === 501) {
        state.preview = true;
        notify(`${description} saved in preview mode. API unavailable: ${error.message}`, "info");
        return "preview";
      }
      notify(`${description} failed: ${error.message}`, "error");
      return null;
    }
  }
  async function loadBackendData() {
    if (session?.role === "student") {
      try {
        const payload = await apiRequest("portal/me");
        state.portal = payload;
        state.students = [payload.profile];
        state.courses = payload.courses || [];
        state.attendance[today] ||= {};
        (payload.attendance || []).filter(record => record.date === today).forEach(record => {
          state.attendance[today][record.student_id] = record.status;
        });
        state.preview = false;
        render();
      } catch (error) {
        if (error.status === 401) {
          session = null;
          localStorage.removeItem(SESSION_KEY);
          currentPage = "login";
          render();
        }
        notify(`Could not load your student portal: ${error.message}`, "error");
      }
      return;
    }
    const resources = ["students", "teachers", "courses"];
    const failures = [];
    const results = await Promise.all(resources.map(async resource => {
      try {
        const payload = await apiRequest(resource);
        const rows = Array.isArray(payload) ? payload : payload?.[resource];
        if (Array.isArray(rows)) state[resource] = rows;
        return true;
      } catch (error) {
        failures.push(error);
        console.info(`Using preview ${resource}; API unavailable: ${error.message}`);
        return false;
      }
    }));
    let attendanceLoaded = false;
    try {
      const payload = await apiRequest(`attendance?date=${encodeURIComponent(today)}`);
      const records = Array.isArray(payload) ? payload : payload?.attendance;
      if (Array.isArray(records)) {
        state.attendance[today] ||= {};
        records.forEach(record => { state.attendance[today][record.student_id || record.studentId] = record.status; });
        attendanceLoaded = true;
      }
    } catch (error) {
      failures.push(error);
      console.info(`Using preview attendance; API unavailable: ${error.message}`);
    }
    let reportsLoaded = false;
    try {
      const payload = await apiRequest("reports/performance");
      const monthly = payload?.monthly_scores || payload?.monthly;
      const byCourse = payload?.attendance_by_course || payload?.attendanceByCourse;
      const trends = payload?.enrollment_trends || payload?.enrollmentTrends;
      if (Array.isArray(monthly)) state.reports.monthly = monthly;
      if (Array.isArray(byCourse)) state.reports.attendanceByCourse = byCourse;
      if (Array.isArray(trends)) state.reports.enrollmentTrends = trends;
      state.reports.preview = !(Array.isArray(monthly) && Array.isArray(byCourse) && Array.isArray(trends));
      reportsLoaded = !state.reports.preview;
    } catch (error) {
      failures.push(error);
      console.info(`Using preview performance reports; API unavailable: ${error.message}`);
    }
    try {
      state.dashboard = await apiRequest("dashboard");
    } catch (error) {
      failures.push(error);
      console.info(`Dashboard summary unavailable: ${error.message}`);
    }
    state.preview = !(results.every(Boolean) && attendanceLoaded && reportsLoaded && state.dashboard);
    if (failures.some(error => error.status === 401)) {
      session = null;
      localStorage.removeItem(SESSION_KEY);
      currentPage = "login";
    }
    render();
  }
  function changePage(page) {
    currentPage = page;
    searchTerm = "";
    document.querySelectorAll(".sidebar").forEach(el => el.classList.remove("open"));
    document.querySelectorAll(".mobile-overlay").forEach(el => el.classList.remove("show"));
    render();
  }
  const pageInfo = {
    dashboard: ["Overview", "Good morning, Alex 👋"],
    students: ["Students", "Student directory"],
    teachers: ["Teachers", "Teaching team"],
    courses: ["Courses", "Programs & enrollment"],
    attendance: ["Attendance", "Daily attendance"],
    fees: ["Fee management", "Payments & balances"],
    reports: ["Reports", "Performance insights"],
    portal: ["Student portal", "Your campus, at a glance"]
  };
  function navLink(page, label, iconName, count) {
    return `<a class="nav-link ${currentPage === page ? "active" : ""}" href="#${page}" data-page="${page}">${icon(iconName)}<span>${label}</span>${count ? `<span class="nav-count">${count}</span>` : ""}</a>`;
  }
  function shell(content) {
    const info = pageInfo[currentPage] || pageInfo.dashboard;
    const displayName = session?.role === "student" ? currentStudent()?.name || session.name : session?.name || "Alex Morgan";
    const roleLabel = session?.role === "student" ? "Student" : session?.role === "teacher" ? "Teacher" : "Administrator";
    const initialsText = initials(displayName);
    return `<div class="app-shell">
      <aside class="sidebar" id="sidebar">
        <a class="brand" href="#dashboard"><span class="brand-mark">${icon("bookOpen")}</span><span>campus<span>ly</span></span></a>
        <div class="nav-label">Workspace</div>
        <nav class="nav-list" aria-label="Main navigation">
          ${session?.role === "student" ? navLink("portal", "My portal", "grid") : session?.role === "teacher" ? `
          ${navLink("dashboard", "Dashboard", "grid")}
          ${navLink("students", "Students", "users", state.students.length)}
          ${navLink("courses", "My courses", "book", state.courses.length)}
          ${navLink("attendance", "Attendance", "calendar")}
          ${navLink("reports", "Reports", "chart")}` : `
          ${navLink("dashboard", "Dashboard", "grid")}
          ${navLink("students", "Students", "users", state.students.length)}
          ${navLink("teachers", "Teachers", "user", state.teachers.length)}
          ${navLink("courses", "Courses", "book", state.courses.length)}
          ${navLink("attendance", "Attendance", "calendar")}
          ${navLink("fees", "Fee management", "wallet")}
          ${navLink("reports", "Reports", "chart")}`}
        </nav>
        <div class="sidebar-bottom">
          <div class="help-card"><div class="help-icon">${icon("help")}</div><strong>Need a hand?</strong><p>Our campus support team is always here to help.</p></div>
          <div class="profile-mini"><span class="avatar">${escapeHtml(initialsText)}</span><div class="profile-name">${escapeHtml(displayName)}<span class="profile-role">${roleLabel} account</span></div></div>
        </div>
      </aside>
      <div class="mobile-overlay" id="mobile-overlay"></div>
      <main class="main">
        <header class="topbar">
          <div class="top-left">
            <button class="icon-button menu-toggle" id="menu-toggle" aria-label="Open menu">${icon("grid")}</button>
            <div><div class="eyebrow">Campusly / ${escapeHtml(info[0])}</div><h1 class="page-title">${escapeHtml(info[0])}</h1></div>
          </div>
          <div class="top-actions">
            ${session?.role === "student" ? "" : `<label class="searchbox">${icon("search")}<input id="global-search" type="search" placeholder="Search anything..." value="${escapeHtml(searchTerm)}" aria-label="Search current page"></label>`}
            <button class="icon-button notification" id="notification-button" aria-label="Notifications">${icon("bell")}</button>
            <div class="top-user"><span class="avatar">${escapeHtml(initialsText)}</span><span class="top-user-copy">${escapeHtml(displayName)}<small>${roleLabel}</small></span></div>
            <button class="icon-button" id="logout-button" aria-label="Sign out" title="Sign out">${icon("logout")}</button>
          </div>
        </header>
        <section class="page-content" id="page-content">${content}</section>
      </main>
    </div>`;
  }
  function statCard(label, value, iconName, color, note, trend = "") {
    return `<article class="stat-card"><div class="stat-head"><span class="stat-label">${label}</span><span class="stat-icon ${color}">${icon(iconName)}</span></div><div class="stat-value">${value}</div><div class="stat-foot">${trend ? `<span class="trend">${trend}</span>` : ""}<span>${note}</span></div></article>`;
  }
  function studentRow(student, actions = canManage()) {
    const tone = ["purple", "green", "orange", "blue"].includes(student.tone) ? student.tone : "purple";
    return `<tr>
      <td><div class="student-cell"><span class="avatar ${tone}">${escapeHtml(student.initials || initials(student.name))}</span><div><strong>${escapeHtml(student.name)}</strong><small>${escapeHtml(student.email)}</small></div></div></td>
      <td>${escapeHtml(student.id)}</td><td>${escapeHtml(student.course || student.department)}</td>
      <td><span class="badge ${student.status === "Active" ? "success" : "neutral"}">${escapeHtml(student.status || "Active")}</span></td>
      <td>${Number(student.attendance || 0)}%</td>
      <td>${actions ? `<div class="table-actions"><button class="mini-action" data-action="view" data-id="${escapeHtml(student.id)}" aria-label="View ${escapeHtml(student.name)}">${icon("eye")}</button><button class="mini-action" data-action="edit" data-id="${escapeHtml(student.id)}" aria-label="Edit ${escapeHtml(student.name)}">${icon("edit")}</button><button class="mini-action" data-action="delete" data-id="${escapeHtml(student.id)}" aria-label="Delete ${escapeHtml(student.name)}">${icon("trash")}</button></div>` : `<div class="table-actions"><button class="mini-action" data-action="view" data-id="${escapeHtml(student.id)}" aria-label="View ${escapeHtml(student.name)}">${icon("eye")}</button></div>`}</td>
    </tr>`;
  }
  function dashboard() {
    const feesTotal = state.students.reduce((sum, student) => sum + Number(student.fee || 0), 0);
    const paidTotal = state.students.reduce((sum, student) => sum + Number(student.paid || 0), 0);
    const feeRate = feesTotal ? Math.round(paidTotal / feesTotal * 100) : 0;
    const summary = state.dashboard || {};
    const averageAttendance = state.students.length ? Math.round(state.students.reduce((sum, student) => sum + Number(student.attendance || 0), 0) / state.students.length) : 0;
    const todaysAttendance = state.attendance[today] || {};
    const todaysStatuses = state.students.map(student => todaysAttendance[student.id] || "Absent");
    const present = todaysStatuses.filter(status => status === "Present").length;
    const absent = todaysStatuses.filter(status => status === "Absent").length;
    const late = todaysStatuses.filter(status => status === "Late").length;
    const attendanceRate = state.students.length ? Math.round(present / state.students.length * 100) : 0;
    const trend = state.reports.enrollmentTrends || [];
    const trendMax = Math.max(40, ...trend.flatMap(item => [Number(item.enrollment || 0), Number(item.graduates || 0)]));
    const chartY = value => 158 - Number(value || 0) / trendMax * 140;
    const chartPath = key => trend.map((item, index) => `${index ? "L" : "M"}${40 + (trend.length > 1 ? index * 565 / (trend.length - 1) : 0)} ${chartY(item[key])}`).join(" ");
    const enrollmentPath = chartPath("enrollment");
    const graduationPath = chartPath("graduates");
    const rows = state.students.slice(0, 5);
    return `<div class="welcome-row"><div><h2>Good morning, ${escapeHtml(session?.name?.split(" ")[0] || "Alex")} 👋</h2><p>Here’s what’s happening across your campus today.</p></div><button class="button" data-action="add-student">${icon("plus")} Add student</button></div>
      ${state.preview ? `<div class="notice">Preview data is active. Connect the Flask API at <strong>${API_BASE}/</strong> to load and save your live campus records.</div>` : ""}
      <div class="stats-grid">
        ${statCard("Total students", Number(summary.total_students ?? state.students.length).toLocaleString(), "users", "purple", "enrolled students")}
        ${statCard("Faculty members", Number(summary.total_teachers ?? state.teachers.length).toLocaleString(), "user", "green", "active teachers")}
        ${statCard("Active courses", Number(summary.total_courses ?? state.courses.length).toLocaleString(), "book", "orange", "across departments")}
        ${statCard("Average attendance", `${Number(summary.attendance?.percent ?? averageAttendance)}%`, "calendar", "blue", "today's recorded attendance")}
        ${summary.fees ? statCard("Fees collected", money(summary.fees.collected), "wallet", "green", `${money(summary.fees.pending)} pending`, `${feeRate}%`) : ""}
      </div>
      <div class="dashboard-grid">
        <article class="panel"><div class="panel-head"><div><h3 class="panel-title">Enrollment overview</h3><p class="panel-subtitle">Student enrollment & graduation trends</p></div><button class="button secondary small" data-page="reports">View reports</button></div>
          <div class="chart-area"><div class="chart-legend"><span><i class="legend-dot"></i>Enrollment</span><span><i class="legend-dot alt"></i>Graduates</span></div>
          <svg class="chart-svg" viewBox="0 0 620 190" role="img" aria-label="Enrollment trend chart">
            <defs><linearGradient id="chartFill" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#8175e8" stop-opacity=".19"/><stop offset="1" stop-color="#8175e8" stop-opacity="0"/></linearGradient></defs>
            ${[0,1,2,3].map(index => { const y = 18 + index * 40; const amount = Math.round(trendMax * (1 - index / 3)); return `<line class="grid-line" x1="38" y1="${y}" x2="610" y2="${y}"/><text x="0" y="${y + 3}">${amount}</text>`; }).join("")}
            <path class="chart-fill" d="${enrollmentPath} L605 158 L40 158 Z"/>
            <path class="chart-line" d="${enrollmentPath}"/>
            <path class="chart-line alt" d="${graduationPath}"/>
            ${trend.map((item,index)=>`<text x="${40 + (trend.length > 1 ? index * 565 / (trend.length - 1) : 0)}" y="177" text-anchor="middle">${escapeHtml(item.month)}</text>`).join("")}
          </svg></div>
        </article>
        <article class="panel"><div class="panel-head"><div><h3 class="panel-title">Today’s attendance</h3><p class="panel-subtitle">Campus-wide attendance snapshot</p></div><button class="mini-action" data-page="attendance" aria-label="View attendance">${icon("more")}</button></div>
          <div class="attendance-body"><div class="attendance-total"><strong>${attendanceRate}%</strong><span>${present} present</span></div><div class="attendance-copy">${present} of ${state.students.length} students marked present today</div><div class="progress-track"><span style="width:${attendanceRate}%"></span></div>
          <div class="attendance-legend"><div class="attendance-row"><span class="attendance-name"><i></i>Present</span><strong>${present} students</strong></div><div class="attendance-row"><span class="attendance-name"><i class="absent"></i>Absent</span><strong>${absent} students</strong></div><div class="attendance-row"><span class="attendance-name"><i class="late"></i>Late</span><strong>${late} students</strong></div><div class="attendance-row"><span class="attendance-name"><i class="leave"></i>Enrolled</span><strong>${state.students.length} students</strong></div></div></div>
        </article>
      </div>
      <div class="bottom-grid">
        <article class="panel"><div class="panel-head"><div><h3 class="panel-title">Recent students</h3><p class="panel-subtitle">Your newest campus members</p></div><button class="button secondary small" data-page="students">View all ${icon("chart")}</button></div>
          <div class="table-wrap"><table><thead><tr><th>Student</th><th>Student ID</th><th>Course</th><th>Status</th><th>Attendance</th><th></th></tr></thead><tbody>${rows.length ? rows.map(s => studentRow(s)).join("") : `<tr><td class="table-empty" colspan="6">No students yet. Add a student to get started.</td></tr>`}</tbody></table></div>
        </article>
        <article class="panel"><div class="panel-head"><div><h3 class="panel-title">Program enrollment</h3><p class="panel-subtitle">Current records by course</p></div><button class="button secondary small" data-page="courses">View courses</button></div><div class="activity-list">
          ${state.courses.slice(0,5).map(course => `<div class="activity-item"><span class="activity-mark">${icon("book")}</span><div class="activity-copy" style="flex:1"><div class="attendance-row"><strong>${escapeHtml(course.name)}</strong><strong>${Number(course.students || 0)} / ${Number(course.capacity || 0)}</strong></div><div class="progress-track" style="height:5px;margin:8px 0 0"><span style="width:${Math.min(100, course.capacity ? course.students / course.capacity * 100 : 0)}%"></span></div></div></div>`).join("") || `<div class="table-empty">No course enrollment records yet.</div>`}
        </div></article>
      </div>`;
  }
  function sectionHeader(title, subtitle, action, filters = "") {
    return `<div class="section-heading"><div><h2>${title}</h2><p>${subtitle}</p></div><div class="section-actions">${filters}${action || ""}</div></div>`;
  }
  function tablePanel(title, subtitle, headers, body) {
    return `<article class="panel list-panel"><div class="panel-head"><div><h3 class="panel-title">${title}</h3><p class="panel-subtitle">${subtitle}</p></div></div><div class="table-wrap"><table><thead><tr>${headers.map(h => `<th>${h}</th>`).join("")}</tr></thead><tbody>${body}</tbody></table></div></article>`;
  }
  function matchesSearch(item) {
    return !searchTerm || Object.values(item).some(value => String(value).toLowerCase().includes(searchTerm.toLowerCase()));
  }
  function studentsPage() {
    const students = state.students.filter(matchesSearch);
    const body = students.length ? students.map(student => studentRow(student)).join("") : `<tr><td class="table-empty" colspan="6">No students match your search.</td></tr>`;
    return `${sectionHeader("All students", `${state.students.length} enrolled students across all departments.`, canManage() ? `<button class="button" data-action="add-student">${icon("plus")} Add student</button>` : "", `<select class="filter-select" id="student-department"><option value="">All departments</option>${[...new Set(state.students.map(s => s.department))].map(d => `<option>${escapeHtml(d)}</option>`).join("")}</select>`)}
      <div id="students-table">${tablePanel("Student directory", "Manage student profiles, enrollment, and academic progress.", ["Student", "Student ID", "Course", "Status", "Attendance", "Actions"], body)}</div>`;
  }
  function teachersPage() {
    const rows = state.teachers.filter(matchesSearch).map(teacher => `<tr><td><div class="student-cell"><span class="avatar ${escapeHtml(teacher.tone || "blue")}">${escapeHtml(teacher.initials || initials(teacher.name))}</span><div><strong>${escapeHtml(teacher.name)}</strong><small>${escapeHtml(teacher.email)}</small></div></div></td><td>${escapeHtml(teacher.id)}</td><td>${escapeHtml(teacher.department)}</td><td>${escapeHtml(teacher.subject)}</td><td>${escapeHtml(teacher.experience || "—")}</td><td><span class="badge success">${escapeHtml(teacher.status || "Active")}</span></td><td>${canManage() ? `<div class="table-actions"><button class="mini-action" data-action="view-teacher" data-id="${escapeHtml(teacher.id)}" aria-label="View teacher">${icon("eye")}</button><button class="mini-action" data-action="edit-teacher" data-id="${escapeHtml(teacher.id)}" aria-label="Edit teacher">${icon("edit")}</button><button class="mini-action" data-action="delete-teacher" data-id="${escapeHtml(teacher.id)}" aria-label="Delete teacher">${icon("trash")}</button></div>` : ""}</td></tr>`).join("");
    return `${sectionHeader("Faculty directory", `${state.teachers.length} teachers across ${new Set(state.teachers.map(t => t.department)).size} departments.`, canManage() ? `<button class="button" data-action="add-teacher">${icon("plus")} Add teacher</button>` : "")}
      ${tablePanel("Teaching team", "Manage teacher profiles and assigned subjects.", ["Teacher", "Faculty ID", "Department", "Assigned subject", "Experience", "Status", "Actions"], rows || `<tr><td class="table-empty" colspan="7">No teachers match your search.</td></tr>`)}`;
  }
  function coursesPage() {
    const courses = state.courses.filter(matchesSearch);
    return `${sectionHeader("Courses & programs", `${state.courses.length} active programs offered across your campus.`, canManage() ? `<button class="button" data-action="add-course">${icon("plus")} Add course</button>` : "", `<select class="filter-select" id="course-department"><option value="">All departments</option>${[...new Set(state.courses.map(c => c.department))].map(d => `<option>${escapeHtml(d)}</option>`).join("")}</select>`)}
      <div class="course-grid">${courses.length ? courses.map(course => `<article class="course-card"><div class="course-card-top"><span class="course-symbol">${escapeHtml(course.symbol || course.name.slice(0,2).toUpperCase())}</span>${canManage() ? `<div class="table-actions"><button class="mini-action" data-action="edit-course" data-id="${escapeHtml(course.id)}" aria-label="Edit course">${icon("edit")}</button><button class="mini-action" data-action="delete-course" data-id="${escapeHtml(course.id)}" aria-label="Delete course">${icon("trash")}</button></div>` : ""}</div><h3>${escapeHtml(course.name)}</h3><p>${escapeHtml(course.department)} · ${escapeHtml(course.duration || "")}</p><div class="course-meta"><span>Lead instructor</span><strong>${escapeHtml(course.teacher || "Unassigned")}</strong></div><div class="course-meta" style="border-top:0;padding-top:8px;margin-top:0"><span>Student enrollment</span><strong>${Number(course.students || 0)} / ${Number(course.capacity || 0)}</strong></div><div class="course-meter"><span style="width:${Math.min(100, course.capacity ? course.students / course.capacity * 100 : 0)}%"></span></div></article>`).join("") : `<article class="panel table-empty">No courses match your search.</article>`}</div>`;
  }
  function attendancePage() {
    const rows = state.students.filter(matchesSearch).map(student => {
      const status = state.attendance[attendanceDate]?.[student.id] || "Absent";
      return `<tr><td><div class="student-cell"><span class="avatar ${escapeHtml(student.tone || "purple")}">${escapeHtml(student.initials || initials(student.name))}</span><div><strong>${escapeHtml(student.name)}</strong><small>${escapeHtml(student.id)}</small></div></div></td><td>${escapeHtml(student.department)}</td><td>${escapeHtml(student.course)}</td><td><div class="attendance-mark">${["Present", "Absent", "Late"].map(value => `<button class="${status === value ? `selected ${value.toLowerCase()}` : ""}" data-action="mark-attendance" data-id="${escapeHtml(student.id)}" data-status="${value}">${value}</button>`).join("")}</div></td></tr>`;
    }).join("");
    return `${sectionHeader("Daily attendance", "Mark and review student attendance for a selected day.", `<button class="button" data-action="save-attendance">${icon("check")} Save attendance</button>`)}
      <div class="panel"><div class="attendance-toolbar"><div class="left"><strong>Attendance register</strong><span class="muted">${state.students.length} students</span></div><input id="attendance-date" type="date" value="${attendanceDate}" aria-label="Attendance date"></div>
      <div class="table-wrap"><table><thead><tr><th>Student</th><th>Department</th><th>Course</th><th>Mark attendance</th></tr></thead><tbody>${rows || `<tr><td class="table-empty" colspan="4">No students to display.</td></tr>`}</tbody></table></div></div>`;
  }
  function feesPage() {
    const students = state.students.filter(matchesSearch);
    const total = state.students.reduce((sum,s) => sum + Number(s.fee || 0),0);
    const collected = state.students.reduce((sum,s) => sum + Number(s.paid || 0),0);
    const pending = total - collected;
    const rows = students.map(s => {
      const due = Math.max(0, Number(s.fee || 0) - Number(s.paid || 0));
      const status = due === 0 ? ["Paid","success"] : Number(s.paid || 0) > 0 ? ["Partial","warning"] : ["Unpaid","danger"];
      return `<tr><td><div class="student-cell"><span class="avatar ${escapeHtml(s.tone || "purple")}">${escapeHtml(s.initials || initials(s.name))}</span><div><strong>${escapeHtml(s.name)}</strong><small>${escapeHtml(s.id)}</small></div></div></td><td>${escapeHtml(s.course)}</td><td>${money(s.fee)}</td><td>${money(s.paid)}</td><td><strong>${money(due)}</strong></td><td><span class="badge ${status[1]}">${status[0]}</span></td><td>${due ? `<button class="button secondary small" data-action="record-payment" data-id="${escapeHtml(s.id)}">Record payment</button>` : "—"}</td></tr>`;
    }).join("");
    return `${sectionHeader("Fee management", "Track tuition, payment status, and outstanding balances.", `<button class="button secondary" data-action="export-fees">${icon("download")} Export CSV</button>`)}
      <div class="report-summary"><div class="report-tile"><span>Total billed</span><strong>${money(total)}</strong><small>Across ${state.students.length} students</small></div><div class="report-tile"><span>Collected</span><strong>${money(collected)}</strong><small>Current academic year</small></div><div class="report-tile"><span>Pending fees</span><strong>${money(pending)}</strong><small>${state.students.filter(s=>s.paid<s.fee).length} students with balance</small></div></div>
      ${tablePanel("Student fee ledger", "Review balances and record payments.", ["Student", "Program", "Total fee", "Paid", "Balance", "Status", "Action"], rows || `<tr><td class="table-empty" colspan="7">No students match your search.</td></tr>`)}`;
  }
  function reportsPage() {
    const avg = state.students.length ? Math.round(state.students.reduce((sum,s)=>sum+Number(s.attendance || 0),0)/state.students.length) : 0;
    const atRisk = state.students.filter(s => Number(s.attendance || 0) < 80).length;
    const complete = state.students.filter(s => Number(s.paid || 0) >= Number(s.fee || 0)).length;
    const monthly = state.reports.monthly || [];
    const courseAttendance = state.reports.attendanceByCourse || [];
    return `${sectionHeader("Reports & insights", "A quick pulse on academic performance and attendance.", `<button class="button secondary" data-action="export-report">${icon("download")} Export report</button>`)}
      ${state.reports.preview ? `<div class="notice">Academic score and course-attendance charts are sample preview data until the reports API is connected.</div>` : ""}
      <div class="report-summary"><div class="report-tile"><span>Average attendance</span><strong>${avg}%</strong><small>Across all enrolled students</small></div><div class="report-tile"><span>Students at risk</span><strong>${atRisk}</strong><small>Attendance below 80%</small></div><div class="report-tile"><span>Fees fully paid</span><strong>${complete} / ${state.students.length}</strong><small>Current academic year</small></div></div>
      <div class="dashboard-grid"><article class="panel"><div class="panel-head"><div><h3 class="panel-title">Academic performance</h3><p class="panel-subtitle">${state.reports.preview ? "Sample assessment scores by month" : "Average assessment score by month"}</p></div><span class="badge neutral">Fall semester</span></div><div class="report-bars">${monthly.map(item=>`<div class="bar-group"><div class="bar-pair"><span class="bar" style="height:${Math.max(0,Math.min(100,Number(item.score || 0)))}%"></span><span class="bar alt" style="height:${Math.max(0,Math.min(100,Number(item.average || 0)))}%"></span></div>${escapeHtml(item.month)}</div>`).join("") || `<div class="table-empty">No academic performance data is available.</div>`}</div><div class="report-legend"><span><i class="legend-dot"></i>Assessment scores</span><span><i class="legend-dot alt"></i>Class average</span></div></article>
      <article class="panel"><div class="panel-head"><div><h3 class="panel-title">Attendance by course</h3><p class="panel-subtitle">Student engagement snapshot</p></div></div><div class="activity-list">${courseAttendance.slice(0,5).map(item=>`<div class="activity-item"><div style="flex:1"><div class="attendance-row"><strong>${escapeHtml(item.course || item.name)}</strong><strong>${Number(item.attendance || 0)}%</strong></div><div class="progress-track" style="height:5px;margin:9px 0 0"><span style="width:${Math.max(0,Math.min(100,Number(item.attendance || 0)))}%"></span></div></div></div>`).join("") || `<div class="table-empty">Add courses to see attendance insights.</div>`}</div></article></div>
      ${tablePanel("Student performance overview", "Attendance and fee completion by student.", ["Student", "Program", "Attendance", "Fee status", "Academic status"], state.students.map(s=>`<tr><td><div class="student-cell"><span class="avatar ${escapeHtml(s.tone || "purple")}">${escapeHtml(s.initials || initials(s.name))}</span><div><strong>${escapeHtml(s.name)}</strong><small>${escapeHtml(s.id)}</small></div></div></td><td>${escapeHtml(s.course)}</td><td><span class="badge ${s.attendance >= 85 ? "success" : s.attendance >= 75 ? "warning" : "danger"}">${Number(s.attendance || 0)}%</span></td><td>${Number(s.paid || 0) >= Number(s.fee || 0) ? `<span class="badge success">Paid</span>` : `<span class="badge warning">Balance due</span>`}</td><td>${Number(s.attendance || 0) < 75 ? `<span class="badge danger">Needs support</span>` : `<span class="badge success">On track</span>`}</td></tr>`).join("") || `<tr><td class="table-empty" colspan="5">No student data available.</td></tr>`)}`;
  }
  function portalPage() {
    const student = state.portal?.profile || currentStudent();
    if (!student) return `<div class="panel table-empty">Loading your secure student portal…</div>`;
    const paid = Number(student.paid || 0);
    const due = Math.max(0, Number(student.fee || 0) - paid);
    const courses = state.portal?.courses || state.courses.filter(c => c.name === student.course);
    const feeAccounts = state.portal?.fees || [];
    const hasFees = feeAccounts.length > 0 || !state.portal && Number(student.fee || 0) > 0;
    const attendanceRecords = (state.portal?.attendance || []).slice(0, 5);
    const results = state.portal?.results || [];
    return `<div class="portal-banner"><div><h2>Welcome back, ${escapeHtml(student.name.split(" ")[0])}!</h2><p>Your student portal — everything you need to stay on track.</p></div><span class="avatar">${escapeHtml(student.initials || initials(student.name))}</span></div>
      ${state.preview ? `<div class="notice">You’re viewing preview portal data. Once connected, your profile and records will load securely from the campus API.</div>` : ""}
      <div class="stats-grid">${statCard("Attendance", `${Number(student.attendance || 0)}%`, "calendar", "purple", "your overall record", Number(student.attendance || 0) >= 80 ? "On track" : "Needs attention")}${statCard("Current courses", String(courses.length), "book", "blue", "this semester", courses.length ? "Enrolled" : "None")}${statCard("Fees paid", hasFees ? money(paid) : "—", "wallet", "green", "this academic year", hasFees ? due ? "In progress" : "Complete" : "No account")}${statCard("Outstanding balance", hasFees ? money(due) : "—", "wallet", "orange", due ? "Payment due" : hasFees ? "All clear" : "No account", due ? "Due" : "")}</div>
      <div class="portal-content"><article class="panel"><div class="panel-head"><div><h3 class="panel-title">My profile</h3><p class="panel-subtitle">Your personal and academic information</p></div><button class="mini-action" data-action="view-portal-profile" aria-label="View full profile">${icon("eye")}</button></div><div class="portal-kv"><div><span>Full name</span><strong>${escapeHtml(student.name)}</strong></div><div><span>Student ID</span><strong>${escapeHtml(student.id)}</strong></div><div><span>Email</span><strong>${escapeHtml(student.email)}</strong></div><div><span>Phone</span><strong>${escapeHtml(student.phone || "Not provided")}</strong></div><div><span>Department</span><strong>${escapeHtml(student.department)}</strong></div><div><span>Year</span><strong>${escapeHtml(student.year || "Enrolled")}</strong></div></div></article>
      <article class="panel"><div class="panel-head"><div><h3 class="panel-title">My courses</h3><p class="panel-subtitle">${courses.length} current course${courses.length === 1 ? "" : "s"}</p></div></div><div class="activity-list">${courses.map(course => `<div class="activity-item"><span class="activity-mark">${icon("book")}</span><div class="activity-copy"><strong>${escapeHtml(course.name)}</strong><small>${escapeHtml(course.department)} · ${escapeHtml(course.teacher || "Instructor to be assigned")}${course.duration ? ` · ${escapeHtml(course.duration)}` : ""}</small></div></div>`).join("") || `<div class="table-empty">No course enrollments are recorded.</div>`}</div></article>
      <article class="panel"><div class="panel-head"><div><h3 class="panel-title">Attendance record</h3><p class="panel-subtitle">Overall attendance and recent daily marks</p></div></div><div class="portal-kv"><div><span>Overall attendance</span><strong>${Number(student.attendance || 0)}%</strong></div><div><span>Today’s status</span><strong>${escapeHtml(state.attendance[today]?.[student.id] || "Not marked")}</strong></div><div><span>Attendance goal</span><strong>At least 85%</strong></div><div><span>Standing</span><strong>${Number(student.attendance || 0) >= 85 ? "On track" : "Needs improvement"}</strong></div></div><div class="activity-list">${attendanceRecords.map(record => `<div class="activity-item"><div class="activity-copy" style="flex:1"><div class="attendance-row"><span>${escapeHtml(record.date)}</span><span class="badge ${record.status === "Present" ? "success" : record.status === "Late" ? "warning" : "danger"}">${escapeHtml(record.status)}</span></div></div></div>`).join("") || `<div class="table-empty">No attendance records are available.</div>`}</div></article>
      <article class="panel"><div class="panel-head"><div><h3 class="panel-title">Fee summary</h3><p class="panel-subtitle">Tuition balances and payment history</p></div></div><div class="portal-kv"><div><span>Total tuition</span><strong>${hasFees ? money(student.fee) : "No fee account"}</strong></div><div><span>Amount paid</span><strong>${hasFees ? money(paid) : "—"}</strong></div><div><span>Balance remaining</span><strong>${hasFees ? money(due) : "—"}</strong></div><div><span>Payment status</span><strong>${hasFees ? due ? "Payment pending" : "Paid in full" : "Not billed"}</strong></div></div>${feeAccounts.map(account => `<div class="activity-list"><div class="activity-item"><div class="activity-copy"><strong>${escapeHtml(account.period)}</strong><small>${money(account.paid)} paid · ${money(account.balance)} outstanding</small></div></div></div>`).join("")}</article>
      <article class="panel"><div class="panel-head"><div><h3 class="panel-title">Academic results</h3><p class="panel-subtitle">Recorded assessment scores</p></div></div><div class="activity-list">${results.slice(0,6).map(result => `<div class="activity-item"><span class="activity-mark blue">${icon("chart")}</span><div class="activity-copy"><strong>${escapeHtml(result.assessment)}</strong><small>${escapeHtml(result.course)} · ${escapeHtml(result.term)} · ${Number(result.percentage || 0)}%</small></div></div>`).join("") || `<div class="table-empty">No academic results have been recorded.</div>`}</div></article></div>`;
  }
  function loginPage() {
    return `<div class="login-screen"><section class="login-art"><a class="brand" href="#"><span class="brand-mark">${icon("bookOpen")}</span><span>campus<span>ly</span></span></a><div class="login-copy"><div class="eyebrow">A better way to learn & lead</div><h1>Everything campus,<br>in one place.</h1><p>Manage your campus community with clarity. From student records to academic insights, campus life runs smoother here.</p></div><div class="login-feature">✦ &nbsp;Designed for modern campus communities</div></section><section class="login-panel"><form class="login-form" id="login-form"><h2>Welcome back</h2><p>Sign in to your account to continue to your campus workspace.</p><div class="form-field"><label for="login-role">I am signing in as</label><select id="login-role" name="role"><option value="admin">Administrator</option><option value="teacher">Teacher</option><option value="student">Student</option></select></div><div class="form-field"><label for="login-identity">Email address or student ID</label><input id="login-identity" name="identity" autocomplete="username" required placeholder="you@campus.edu"></div><div class="form-field"><label for="login-password">Password</label><input id="login-password" name="password" type="password" autocomplete="current-password" required placeholder="Enter your password"></div><button class="button" type="submit">Sign in to Campusly ${icon("logout")}</button><div class="demo-credentials"><strong>Secure sign-in</strong><br>Use the account and password provided by your campus administrator.</div></form></section></div>`;
  }
  function render() {
    const root = document.getElementById("app");
    if (!session || currentPage === "login") {
      root.innerHTML = loginPage();
      bindLogin();
      return;
    }
    if (session.role === "student" && currentPage !== "portal") currentPage = "portal";
    if (session.role === "teacher" && ["fees", "teachers"].includes(currentPage)) currentPage = "dashboard";
    const views = { dashboard, students: studentsPage, teachers: teachersPage, courses: coursesPage, attendance: attendancePage, fees: feesPage, reports: reportsPage, portal: portalPage };
    root.innerHTML = shell((views[currentPage] || dashboard)());
    bindShell();
    if (currentPage === "students") bindDepartmentFilter("student-department", "students", studentsPage);
    if (currentPage === "courses") bindDepartmentFilter("course-department", "courses", coursesPage);
  }
  function bindLogin() {
    document.getElementById("login-role").addEventListener("change", event => {
      const identity = document.getElementById("login-identity");
      const password = document.getElementById("login-password");
      identity.placeholder = event.target.value === "student" ? "Student ID or email" : "you@campus.edu";
      password.value = "";
    });
    document.getElementById("login-form").addEventListener("submit", async event => {
      event.preventDefault();
      const form = new FormData(event.currentTarget);
      const role = form.get("role");
      const identity = String(form.get("identity")).trim();
      const password = String(form.get("password"));
      try {
        const response = await apiRequest("auth/login", { method: "POST", body: JSON.stringify({ role, identity, password }) });
        if (!response?.token) throw new Error("The sign-in response did not include a session token.");
        session = { role: response.role || role, name: response.name || identity, studentId: response.student_id, token: response.token };
        localStorage.setItem(SESSION_KEY, JSON.stringify(session));
        currentPage = session.role === "student" ? "portal" : "dashboard";
        state.portal = null;
        render();
        notify("You’re signed in.");
        await loadBackendData();
      } catch (error) {
        notify(`Sign-in failed: ${error.message}`, "error");
      }
    });
  }
  function bindShell() {
    document.querySelectorAll("[data-page]").forEach(el => el.addEventListener("click", event => {
      event.preventDefault();
      if (session?.role === "student" && el.dataset.page !== "portal") return;
      changePage(el.dataset.page);
    }));
    document.getElementById("global-search")?.addEventListener("input", event => {
      searchTerm = event.target.value;
      const focused = true;
      render();
      const search = document.getElementById("global-search");
      if (focused && search) { search.focus(); search.setSelectionRange(search.value.length, search.value.length); }
    });
    document.getElementById("logout-button").addEventListener("click", () => {
      session = null;
      localStorage.removeItem(SESSION_KEY);
      currentPage = "login";
      render();
      notify("You have signed out.", "info");
    });
    document.getElementById("notification-button").addEventListener("click", () => notify(state.preview ? "Preview mode: no live notifications are connected." : "You’re all caught up.", "info"));
    document.getElementById("menu-toggle").addEventListener("click", () => {
      document.getElementById("sidebar").classList.toggle("open");
      document.getElementById("mobile-overlay").classList.toggle("show");
    });
    document.getElementById("mobile-overlay").addEventListener("click", () => {
      document.getElementById("sidebar").classList.remove("open");
      document.getElementById("mobile-overlay").classList.remove("show");
    });
    document.getElementById("page-content").addEventListener("click", handleAction);
    document.getElementById("page-content").addEventListener("change", event => {
      if (event.target.id === "attendance-date") {
        attendanceDate = event.target.value;
        loadAttendanceDate(attendanceDate);
      }
    });
  }
  async function loadAttendanceDate(date) {
    try {
      const payload = await apiRequest(`attendance?date=${encodeURIComponent(date)}`);
      const records = Array.isArray(payload) ? payload : payload?.attendance;
      if (!Array.isArray(records)) throw new Error("The attendance response must contain an array of records.");
      state.attendance[date] = {};
      records.forEach(record => { state.attendance[date][record.student_id || record.studentId] = record.status; });
      saveState();
      render();
    } catch (error) {
      if (error.status && error.status !== 404 && error.status !== 501) {
        notify(`Could not load attendance: ${error.message}`, "error");
        return;
      }
      if (!state.attendance[date]) state.attendance[date] = {};
      if (date !== today) notify(`No live attendance record for ${date}; showing the local preview register.`, "info");
      render();
    }
  }
  function bindDepartmentFilter(id, resource, view) {
    document.getElementById(id)?.addEventListener("change", event => {
      const query = event.target.value;
      const list = state[resource];
      const filtered = list.filter(item => (!query || item.department === query) && (!searchTerm || Object.values(item).some(v => String(v).toLowerCase().includes(searchTerm.toLowerCase()))));
      if (resource === "students") {
        const body = filtered.length ? filtered.map(student => studentRow(student)).join("") : `<tr><td class="table-empty" colspan="6">No students in this department.</td></tr>`;
        document.getElementById("students-table").innerHTML = tablePanel("Student directory", "Manage student profiles, enrollment, and academic progress.", ["Student", "Student ID", "Course", "Status", "Attendance", "Actions"], body);
      } else {
        const grid = document.querySelector(".course-grid");
        const html = coursesPage();
        const detached = document.createElement("div"); detached.innerHTML = html;
        const cards = [...detached.querySelectorAll(".course-card")].filter(card => !query || card.textContent.includes(query));
        grid.innerHTML = cards.length ? cards.map(card => card.outerHTML).join("") : `<article class="panel table-empty">No courses in this department.</article>`;
      }
    });
  }
  function handleAction(event) {
    const target = event.target.closest("[data-action]");
    if (!target) return;
    const { action, id } = target.dataset;
    if (action === "add-student") return openRecordForm("student");
    if (action === "add-teacher") return openRecordForm("teacher");
    if (action === "add-course") return openRecordForm("course");
    if (action === "view") return viewStudent(id);
    if (action === "edit") return openRecordForm("student", byId(state.students, id));
    if (action === "delete") return deleteRecord("students", id, "student");
    if (action === "view-teacher") return viewTeacher(id);
    if (action === "edit-teacher") return openRecordForm("teacher", byId(state.teachers, id));
    if (action === "delete-teacher") return deleteRecord("teachers", id, "teacher");
    if (action === "edit-course") return openRecordForm("course", byId(state.courses, id));
    if (action === "delete-course") return deleteRecord("courses", id, "course");
    if (action === "mark-attendance") {
      state.attendance[attendanceDate] ||= {};
      state.attendance[attendanceDate][id] = target.dataset.status;
      saveState();
      const row = target.closest("tr");
      row.querySelectorAll("[data-action='mark-attendance']").forEach(button => {
        button.className = button.dataset.status === state.attendance[attendanceDate][id] ? `selected ${button.dataset.status.toLowerCase()}` : "";
      });
      return;
    }
    if (action === "save-attendance") return saveAttendance();
    if (action === "record-payment") return recordPayment(id);
    if (action === "export-fees") return exportCsv("fee-ledger.csv", [["Student", "ID", "Course", "Fee", "Paid", "Balance", "Status"], ...state.students.map(s => [s.name, s.id, s.course, s.fee, s.paid, Math.max(0,s.fee-s.paid), s.paid >= s.fee ? "Paid" : "Pending"])]);
    if (action === "export-report") return exportCsv("student-performance.csv", [["Student", "ID", "Course", "Attendance", "Fee status"], ...state.students.map(s => [s.name,s.id,s.course,`${s.attendance}%`,s.paid >= s.fee ? "Paid" : "Balance due"])]);
    if (action === "view-portal-profile") return viewStudent(currentStudent().id);
  }
  function openModal(title, body) {
    document.getElementById("modal-root").innerHTML = `<div class="modal-backdrop"><section class="modal" role="dialog" aria-modal="true" aria-label="${escapeHtml(title)}"><div class="modal-head"><h3>${escapeHtml(title)}</h3><button class="icon-button" data-action="close-modal" aria-label="Close dialog">${icon("close")}</button></div><div class="modal-body">${body}</div></section></div>`;
    document.querySelector(".modal-backdrop").addEventListener("click", event => {
      if (event.target.classList.contains("modal-backdrop") || event.target.closest("[data-action='close-modal']")) closeModal();
    });
  }
  function closeModal() { document.getElementById("modal-root").innerHTML = ""; }
  function inputField(label, name, value = "", options = {}) {
    const { type = "text", required = true, full = false, choices } = options;
    const control = choices ? `<select id="field-${name}" name="${name}" ${required ? "required" : ""}>${choices.map(choice => `<option ${String(value) === choice ? "selected" : ""}>${escapeHtml(choice)}</option>`).join("")}</select>` : `<input id="field-${name}" name="${name}" type="${type}" value="${escapeHtml(value)}" ${required ? "required" : ""}>`;
    return `<div class="form-field ${full ? "full" : ""}"><label for="field-${name}">${label}</label>${control}</div>`;
  }
  function openRecordForm(type, record = null) {
    const config = {
      student: { resource: "students", title: record ? "Edit student" : "Add a student", fields: [
        ["name","Full name"],["email","Email address","email"],["id","Student ID"],["phone","Phone number","tel"],["department","Department",null,false,["Computer Science","Business","Design"]],["course","Course"],["year","Year of study",null,false,["Year 1","Year 2","Year 3","Year 4"]],["fee","Annual fee","number"],["paid","Amount paid","number"],["attendance","Attendance (%)","number"],["status","Status",null,false,["Active","Inactive"]],["password","Student portal password","password",true]
      ] },
      teacher: { resource: "teachers", title: record ? "Edit teacher" : "Add a teacher", fields: [
        ["name","Full name"],["email","Email address","email"],["id","Faculty ID"],["phone","Phone number","tel"],["department","Department",null,false,["Computer Science","Business","Design"]],["subject","Assigned subject"],["experience","Teaching experience"],["status","Status",null,false,["Active","Inactive"]],["password","Teacher portal password","password",true]
      ] },
      course: { resource: "courses", title: record ? "Edit course" : "Add a course", fields: [
        ["name","Course name"],["id","Course code"],["department","Department",null,false,["Computer Science","Business","Design"]],["teacher","Lead instructor",null,false,state.teachers.map(t=>t.name)],["students","Enrolled students","number"],["capacity","Enrollment capacity","number"],["duration","Program duration"]
      ] }
    }[type];
    const formFields = record && type === "student" ? config.fields.filter(([name]) => !["fee", "paid"].includes(name)) : config.fields;
    const fieldHtml = formFields.map(([name,label,typeName,optional,choices]) => inputField(label, name, record?.[name] ?? (name === "status" ? "Active" : name === "attendance" ? 90 : name === "paid" || name === "students" ? 0 : name === "capacity" ? 100 : ""), { type: typeName || "text", required: !optional, choices })).join("");
    const accountHint = type === "student" || type === "teacher" ? `<p class="form-hint">Portal password is optional. If set, it must contain at least 10 characters. Fee balances are managed in Fee management.</p>` : "";
    openModal(config.title, `<form id="record-form">${accountHint}<div class="form-grid">${fieldHtml}</div><div class="modal-actions"><button type="button" class="button secondary" data-action="close-modal">Cancel</button><button type="submit" class="button">${record ? "Save changes" : "Create record"}</button></div></form>`);
    document.getElementById("record-form").addEventListener("submit", async event => {
      event.preventDefault();
      const data = Object.fromEntries(new FormData(event.currentTarget));
      ["fee","paid","attendance","students","capacity"].forEach(key => { if (data[key] !== undefined) data[key] = Number(data[key]); });
      if (type === "student" || type === "teacher") data.initials = initials(data.name);
      if (type === "student" && !record) data.tone = ["purple","green","orange","blue"][state.students.length % 4];
      if (type === "course") data.symbol = data.name.split(/\s+/).map(w=>w[0]).slice(0,2).join("").toUpperCase();
      const isNew = !record;
      if (type === "student" && isNew && !data.id) data.id = `STU-${Date.now().toString().slice(-5)}`;
      if (type === "teacher" && isNew && !data.id) data.id = `TCH-${Date.now().toString().slice(-5)}`;
      if (type === "course" && isNew && !data.id) data.id = `CRS-${Date.now().toString().slice(-3)}`;
      const result = await persistMutation(record ? `${config.resource}/${encodeURIComponent(record.id)}` : config.resource, {
        method: record ? "PUT" : "POST", body: JSON.stringify(data)
      }, typeLabel(type));
      if (!result) return;
      if (record) Object.assign(record, data);
      else {
        state[config.resource].unshift(data);
        if (type === "student") {
          state.attendance[today] ||= {};
          state.attendance[today][data.id] = "Absent";
        }
      }
      saveState();
      if (result === "api") notify(isNew ? `${typeLabel(type)} created successfully.` : `${typeLabel(type)} updated successfully.`);
      closeModal();
      render();
    });
  }
  const typeLabel = type => ({ student: "Student", teacher: "Teacher", course: "Course" })[type] || "Record";
  function viewStudent(id) {
    const student = byId(state.students, id);
    if (!student) return notify("That student could not be found.", "error");
    const due = Math.max(0, Number(student.fee || 0) - Number(student.paid || 0));
    openModal("Student profile", `<div class="student-cell" style="margin-bottom:18px"><span class="avatar ${escapeHtml(student.tone || "purple")}">${escapeHtml(student.initials || initials(student.name))}</span><div><strong style="font-size:13px">${escapeHtml(student.name)}</strong><small>${escapeHtml(student.id)}</small></div></div><div class="detail-list">${[["Email",student.email],["Phone",student.phone || "—"],["Department",student.department],["Course",student.course],["Year",student.year || "—"],["Status",student.status || "Active"],["Attendance",`${Number(student.attendance || 0)}%`],["Fee balance",money(due)]].map(([label,value])=>`<div class="detail-item"><span>${label}</span><strong>${escapeHtml(value)}</strong></div>`).join("")}</div>`);
  }
  function viewTeacher(id) {
    const teacher = byId(state.teachers, id);
    if (!teacher) return notify("That teacher could not be found.", "error");
    openModal("Teacher profile", `<div class="student-cell" style="margin-bottom:18px"><span class="avatar">${escapeHtml(teacher.initials || initials(teacher.name))}</span><div><strong style="font-size:13px">${escapeHtml(teacher.name)}</strong><small>${escapeHtml(teacher.id)}</small></div></div><div class="detail-list">${[["Email",teacher.email],["Phone",teacher.phone || "—"],["Department",teacher.department],["Assigned subject",teacher.subject],["Experience",teacher.experience || "—"],["Status",teacher.status || "Active"]].map(([label,value])=>`<div class="detail-item"><span>${label}</span><strong>${escapeHtml(value)}</strong></div>`).join("")}</div>`);
  }
  async function deleteRecord(resource, id, label) {
    const record = byId(state[resource], id);
    if (!record || !window.confirm(`Delete ${record.name}? This action cannot be undone.`)) return;
    const result = await persistMutation(`${resource}/${encodeURIComponent(id)}`, { method: "DELETE" }, typeLabel(label));
    if (!result) return;
    state[resource] = state[resource].filter(item => item.id !== id);
    if (resource === "students") Object.values(state.attendance).forEach(records => delete records[id]);
    saveState();
    if (result === "api") notify(`${typeLabel(label)} deleted.`);
    render();
  }
  async function recordPayment(id) {
    const student = byId(state.students, id);
    if (!student) return notify("Student record not found.", "error");
    const remaining = Math.max(0, Number(student.fee || 0) - Number(student.paid || 0));
    const value = window.prompt(`Enter payment amount (balance: ${money(remaining)}):`, String(remaining));
    if (value === null) return;
    const amount = Number(value);
    if (!Number.isFinite(amount) || amount <= 0 || amount > remaining) return notify("Enter a valid payment amount up to the outstanding balance.", "error");
    const newPaid = Number(student.paid || 0) + amount;
    const result = await persistMutation(`fees/${encodeURIComponent(id)}`, { method: "POST", body: JSON.stringify({ student_id: id, amount, paid: newPaid }) }, "Payment");
    if (!result) return;
    student.paid = newPaid;
    saveState();
    if (result === "api") notify(`${money(amount)} payment recorded for ${student.name}.`);
    render();
  }
  async function saveAttendance() {
    const entries = state.students.map(student => ({ student_id: student.id, date: attendanceDate, status: state.attendance[attendanceDate]?.[student.id] || "Absent" }));
    const result = await persistMutation("attendance", { method: "POST", body: JSON.stringify({ date: attendanceDate, records: entries }) }, "Attendance");
    if (result === "api") notify(`Attendance saved for ${entries.length} students.`);
    saveState();
    render();
  }
  function exportCsv(filename, rows) {
    const csv = rows.map(row => row.map(value => `"${String(value ?? "").replace(/"/g, '""')}"`).join(",")).join("\r\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
    const link = document.createElement("a");
    link.href = url; link.download = filename; link.click();
    URL.revokeObjectURL(url);
    notify(`${filename} downloaded.`);
  }

  render();
  if (session?.token) loadBackendData();
})();
