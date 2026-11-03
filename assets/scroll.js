// Scroll edition: reveal-on-scroll, parallax, self-playing gene-birth model
// and news timeline. Reads the same data files as the main site.

(function () {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const { esc, formatTitle } = window.LabFormat;
  const PUBS = window.LabFormat.pubs;
  const up = (src) => src;

  // ---------- gene-birth SVG ----------
  const NS = "http://www.w3.org/2000/svg";
  const svg = document.getElementById("gene-svg");
  const el = (tag, attrs, parent = svg) => {
    const n = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
    parent.appendChild(n);
    return n;
  };
  const text = (x, y, s, cls, attrs = {}, parent = svg) => {
    const t = el("text", { x, y, class: cls || "", "text-anchor": "middle", ...attrs }, parent);
    t.textContent = s;
    return t;
  };
  const star = (cx, cy, r, attrs, parent = svg) => {
    const pts = [];
    for (let i = 0; i < 10; i++) {
      const a = Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * 0.45 : r;
      pts.push(`${cx + rr * Math.cos(a)},${cy - rr * Math.sin(a)}`);
    }
    return el("polygon", { points: pts.join(" "), class: "star pop", ...attrs }, parent);
  };
  // Same geometry as scripts_new_lab_website/make_de_novo_gif.py, scaled x10.
  const YA = 170, YB = 330, ORF = [360, 660], LOST = 480, KEPT = 660, OTHER = [270, 730], TSS = 320;
  const chromosome = (y, label, parent) => {
    el("line", { x1: 20, y1: y, x2: 980, y2: y, class: "bb" }, parent);
    text(5, y + 6, label, "sp", { "text-anchor": "end" }, parent);
    el("rect", { x: 60, y: y - 13, width: 160, height: 26, rx: 4, class: "gene" }, parent);
    el("rect", { x: 800, y: y - 13, width: 140, height: 26, rx: 4, class: "gene" }, parent);
    text(140, y + 38, "gene A", "", { "font-size": 14 }, parent);
    text(870, y + 38, "gene B", "", { "font-size": 14 }, parent);
  };
  const stop = (x, y, parent, attrs = {}) => {
    const g = el("g", { class: "stop", ...attrs }, parent);
    el("line", { x1: x, y1: y - 18, x2: x, y2: y + 18 }, g);
    text(x, y - 26, "stop", "", {}, g);
    return g;
  };

  if (svg) {
    chromosome(YA, "Species A", svg);
    el("rect", { x: ORF[0], y: YA - 11, width: ORF[1] - ORF[0], height: 22, rx: 4, class: "orf", "data-orf": "" });
    OTHER.concat([KEPT]).forEach((x) => stop(x, YA, svg));
    stop(LOST, YA, svg, { "data-until": 2 });
    star(TSS - 10, YA, 13, { "data-from": 1 });
    el("path", { d: `M${TSS} ${YA - 30} l26 0 m-8 -6 l8 6 l-8 6`, stroke: "#2e6f9e", "stroke-width": 3, fill: "none", "data-from": 1 });
    let d = `M${TSS} ${YA - 52}`;
    for (let x = TSS; x <= 700; x += 4) d += ` L${x} ${YA - 52 + 7 * Math.sin(x / 6)}`;
    el("path", { d, class: "rna draw", "data-from": 1 });
    text(510, YA - 72, "transcript", "lbl-blue", { "data-from": 1, "data-until": 2, "font-size": 15 });
    star(ORF[0], YA + 30, 13, { "data-from": 2 });
    star(LOST, YA + 30, 13, { "data-from": 2 });
    text(ORF[0], YA + 62, "ATG", "lbl-accent", { "data-from": 2, "font-size": 14 });
    text(540, YA + 62, "open reading frame", "lbl-accent", { "data-from": 2, "data-until": 4, "font-size": 15 });
    text(540, YA + 62, "de novo gene", "lbl-accent", { "data-from": 4, "font-size": 18 });
    const n = 14, bx = (i) => ORF[0] + 10 + i * (ORF[1] - ORF[0] - 20) / (n - 1), by = (i) => YA - 100 + 9 * Math.sin(i * 1.1);
    el("polyline", { points: [...Array(n).keys()].map((i) => `${bx(i)},${by(i)}`).join(" "), class: "chain", "data-from": 3 });
    for (let i = 0; i < n; i++) {
      el("circle", { cx: bx(i), cy: by(i), r: 9, class: "bead pop", "data-from": 3, style: `transition-delay:${i * 70}ms` });
    }
    text(ORF[1] + 30, YA - 95, "novel protein", "lbl-accent", { "data-from": 3, "text-anchor": "start", "font-size": 15 });
    const B = el("g", { class: "speciesB", "data-from": 4 });
    chromosome(YB, "Species B", B);
    OTHER.concat([LOST, KEPT]).forEach((x) => stop(x, YB, B));
    text(510, YB + 62, "orthologous region, still noncoding", "", { "font-size": 15 }, B);
    ORF.forEach((x) => el("line", { x1: x, y1: YB - 46, x2: x, y2: YA + 76, class: "guide" }, B));
  }

  const setStage = (s) => {
    if (!svg) return;
    svg.querySelectorAll("[data-from]").forEach((n) => {
      const from = Number(n.dataset.from), until = n.dataset.until ? Number(n.dataset.until) : Infinity;
      n.classList.toggle("on", s >= from && s < until);
    });
    svg.querySelectorAll("[data-until]:not([data-from])").forEach((n) => {
      n.style.opacity = s >= Number(n.dataset.until) ? 0 : 1;
      n.style.transition = "opacity .6s";
    });
    const orf = svg.querySelector("[data-orf]");
    orf.classList.toggle("on", s >= 2);
    orf.classList.toggle("solid", s >= 4);
  };
  setStage(0);

  // Plays on its own like the GIF on the classic site (same timing as
  // make_de_novo_gif.py: 40 frames at 12 fps per stage, final stage held twice
  // as long), and pauses while the section is off screen.
  const CAPTIONS = [
    "Ancestral genome. A noncoding region between two genes, interrupted by stop codons.",
    "An enabler mutation creates a promoter, and the noncoding region is transcribed.",
    "Further enabler mutations gain a start codon and remove a stop codon, opening a reading frame.",
    "The open reading frame is translated into a novel protein.",
    "Selection retains the de novo gene, while the sister species keeps the ancestral noncoding sequence.",
  ];
  const STAGE_MS = 40 / 12 * 1000, HOLD_MS = 2 * STAGE_MS;
  const stepNum = document.getElementById("step-num"), stepText = document.getElementById("step-text");
  const dotsBox = document.querySelector(".model .dots");
  let stage = 0, timer = null, visible = false;
  if (dotsBox) {
    dotsBox.innerHTML = CAPTIONS.map((_, i) => `<button role="tab" aria-label="Step ${i + 1}"></button>`).join("");
  }
  const dots = dotsBox ? [...dotsBox.children] : [];
  const show = (s) => {
    stage = s;
    setStage(s);
    if (stepNum) stepNum.textContent = s + 1;
    if (stepText) stepText.textContent = CAPTIONS[s];
    dots.forEach((d, i) => { d.classList.toggle("on", i === s); d.setAttribute("aria-selected", String(i === s)); });
  };
  const schedule = () => {
    clearTimeout(timer);
    if (!visible) return;
    timer = setTimeout(() => { show((stage + 1) % CAPTIONS.length); schedule(); },
      stage === CAPTIONS.length - 1 ? HOLD_MS : STAGE_MS);
  };
  dots.forEach((d, i) => d.addEventListener("click", () => { show(i); schedule(); }));
  show(0);
  const modelCard = document.querySelector(".model-card");
  if (modelCard) {
    new IntersectionObserver(([e]) => {
      const wasVisible = visible;
      visible = e.isIntersecting;
      if (visible && !wasVisible) { show(0); schedule(); }
      if (!visible) clearTimeout(timer);
    }, { threshold: 0.35 }).observe(modelCard);
  }

  // ---------- headline word split ----------
  document.querySelectorAll(".split").forEach((h) => {
    h.innerHTML = h.textContent.trim().split(/\s+/).map((w, i) => `<span class="w" style="--i:${i}">${esc(w)}</span>`).join(" ");
    requestAnimationFrame(() => requestAnimationFrame(() => h.classList.add("in")));
  });

  // ---------- news timeline ----------
  const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  const fmtDate = (d) => { const [y, m] = d.split("-"); return m ? `${MONTHS[Number(m) - 1]} ${y}` : y; };
  const items = (window.NEWS || []).map((n) => ({
    date: n.date, kicker: "Lab news", title: esc(n.title), text: n.text || "",
    img: n.image ? { src: up(n.image.src), alt: n.image.alt || "", photo: n.image.photo } : null,
  })).concat(PUBS.filter((p) => p.date >= "2022").map((p) => {
    const f = (window.NEWS_FIGURES || {})[p.doi];
    return {
      date: p.date, kicker: p.preprint ? "New preprint" : "New paper",
      title: `<a href="https://doi.org/${p.doi}">${formatTitle(p.title)}</a>`, text: `<i>${esc(p.journal)}</i>`,
      img: f ? { src: up("assets/img/news/" + f.file), alt: `${f.label} from ${p.title}` } : null,
    };
  })).sort((a, b) => b.date.localeCompare(a.date));
  const tl = document.getElementById("timeline");
  if (tl) {
    tl.innerHTML = items.map((n) => `<li class="t-item"><div class="t-card">
      <div class="t-date">${fmtDate(n.date)}</div><div class="t-kicker">${n.kicker}</div>
      <h3>${n.title}</h3>${n.text ? `<p>${n.text}</p>` : ""}
      ${n.img ? `<img ${n.img.photo ? 'class="photo"' : ""} src="${n.img.src}" alt="${esc(n.img.alt)}" loading="lazy" onerror="this.remove()">` : ""}
    </div></li>`).join("");
  }

  // ---------- people ----------
  // Mirrors the current-members list in people.html; update both together.
  const PEOPLE = [
    ["Claudio Casola", "Principal Investigator", "casola.jpg"],
    ["Adekola Owoyemi", "Ph.D. candidate, ECCB", "owoyemi.jpg"],
    ["Matthew Marano", "Ph.D. candidate, EEB", "marano.jpg"],
    ["Sierra Sanders", "Ph.D. student, EEB", "sanders.jpg"],
    ["Tori Bowman", "Undergraduate, Biochemistry", null],
    ["Catherine Chaison", "Undergraduate, Genetics", "chaison.jpg"],
    ["Sofia Flores", "Undergraduate, Biochemistry", null],
    ["Sofia Rosas", "Undergraduate, Biochemistry", null],
    ["Sree Harshini Satheeskumar", "Undergraduate", null],
    ["Sten Schmidt", "Undergraduate, Computer Science", null],
    ["Samhita Vemuri", "Undergraduate, Biochemistry", null],
  ];
  const faces = document.getElementById("faces");
  if (faces) {
    faces.innerHTML = PEOPLE.map(([name, role, img], i) => {
      const parts = name.split(" "), initials = parts[0][0] + parts[parts.length - 1][0];
      return `<div class="face" style="--i:${i}"><div class="pic">${img ? `<img src="${up("assets/img/people/" + img)}" alt="${esc(name)}" loading="lazy">` : initials}</div>
        <h3>${esc(name)}</h3><p>${esc(role)}</p></div>`;
    }).join("");
  }

  // ---------- reveal on scroll ----------
  const revealObs = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add("in");
      revealObs.unobserve(e.target);
    });
  }, { threshold: 0.15, rootMargin: "0px 0px -8% 0px" });
  document.querySelectorAll(".reveal, .reveal-side, .t-item, .face").forEach((n) => revealObs.observe(n));

  // ---------- scroll-linked: progress, parallax, spine, nav ----------
  const bar = document.querySelector(".progress span");
  const drifters = [...document.querySelectorAll("[data-drift]")];
  const parallax = [...document.querySelectorAll("[data-parallax]")];
  const fader = document.querySelector("[data-fade]");
  const spine = document.querySelector(".spine span");
  const timeline = document.querySelector(".timeline");
  const navLinks = [...document.querySelectorAll(".bar nav a[href^='#']")];
  const sections = navLinks.map((a) => document.querySelector(a.getAttribute("href")));
  let ticking = false;
  const onScroll = () => {
    const y = window.scrollY, vh = window.innerHeight;
    const max = document.documentElement.scrollHeight - vh;
    bar.style.transform = `scaleX(${max > 0 ? y / max : 0})`;
    if (!reduce) {
      drifters.forEach((n) => { const k = Number(n.dataset.drift); n.style.transform = `translate(${y * k * 0.6}px, ${y * k}px) rotate(${y * k * 0.05}deg)`; });
      parallax.forEach((n) => { n.style.transform = `translateY(${y * Number(n.dataset.parallax)}px) rotate(${y * 0.01}deg)`; });
      if (fader) { const p = Math.min(1, y / (vh * 0.8)); fader.style.opacity = 1 - p * 0.9; fader.style.transform = `translateY(${p * -40}px)`; }
    }
    if (spine && timeline) {
      const r = timeline.getBoundingClientRect();
      const p = Math.min(1, Math.max(0, (vh * 0.6 - r.top) / r.height));
      spine.style.transform = `scaleY(${p})`;
    }
    let current = -1;
    sections.forEach((s, i) => { if (s && s.getBoundingClientRect().top < vh * 0.4) current = i; });
    navLinks.forEach((a, i) => a.classList.toggle("active", i === current));
    ticking = false;
  };
  window.addEventListener("scroll", () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();
})();
