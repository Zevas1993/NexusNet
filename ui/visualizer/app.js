const SVG_NS = "http://www.w3.org/2000/svg";
const DEFAULT_VIEWBOX = { x: -1200, y: -900, w: 2400, h: 1800 };

const dom = {
  modePills: document.getElementById("modePills"),
  sessionInput: document.getElementById("sessionInput"),
  refreshButton: document.getElementById("refreshButton"),
  resetViewButton: document.getElementById("resetViewButton"),
  renderTierSelect: document.getElementById("renderTierSelect"),
  toggleLowPower: document.getElementById("toggleLowPower"),
  toggleDream: document.getElementById("toggleDream"),
  toggleCritique: document.getElementById("toggleCritique"),
  toggleConsequence: document.getElementById("toggleConsequence"),
  togglePhysiology: document.getElementById("togglePhysiology"),
  filterRegistryLayer: document.getElementById("filterRegistryLayer"),
  filterSubject: document.getElementById("filterSubject"),
  filterTeacherPair: document.getElementById("filterTeacherPair"),
  filterPromotionKind: document.getElementById("filterPromotionKind"),
  filterTakeoverStatus: document.getElementById("filterTakeoverStatus"),
  filterBenchmarkFamily: document.getElementById("filterBenchmarkFamily"),
  filterThresholdSet: document.getElementById("filterThresholdSet"),
  filterEvidenceBundle: document.getElementById("filterEvidenceBundle"),
  filterDisagreement: document.getElementById("filterDisagreement"),
  filterLineage: document.getElementById("filterLineage"),
  filterTraceWindow: document.getElementById("filterTraceWindow"),
  filterSafePosture: document.getElementById("filterSafePosture"),
  fxCanvas: document.getElementById("fxCanvas"),
  sceneSvg: document.getElementById("sceneSvg"),
  cameraLayer: document.getElementById("cameraLayer"),
  gridLayer: document.getElementById("gridLayer"),
  loopLayer: document.getElementById("loopLayer"),
  linkLayer: document.getElementById("linkLayer"),
  nodeLayer: document.getElementById("nodeLayer"),
  overlayLayer: document.getElementById("overlayLayer"),
  livePosture: document.getElementById("livePosture"),
  legend: document.getElementById("legend"),
  selectionCard: document.getElementById("selectionCard"),
  evidenceCard: document.getElementById("evidenceCard"),
  governanceCard: document.getElementById("governanceCard"),
  compareBundleLeft: document.getElementById("compareBundleLeft"),
  compareBundleRight: document.getElementById("compareBundleRight"),
  compareBundleButton: document.getElementById("compareBundleButton"),
  compareDisagreementLeft: document.getElementById("compareDisagreementLeft"),
  compareDisagreementRight: document.getElementById("compareDisagreementRight"),
  compareDisagreementButton: document.getElementById("compareDisagreementButton"),
  compareReplacementLeft: document.getElementById("compareReplacementLeft"),
  compareReplacementRight: document.getElementById("compareReplacementRight"),
  compareReplacementButton: document.getElementById("compareReplacementButton"),
  compareRouteButton: document.getElementById("compareRouteButton"),
  compareGooseGatewayLeft: document.getElementById("compareGooseGatewayLeft"),
  compareGooseGatewayRight: document.getElementById("compareGooseGatewayRight"),
  compareGooseGatewayButton: document.getElementById("compareGooseGatewayButton"),
  compareGoosePolicyLeft: document.getElementById("compareGoosePolicyLeft"),
  compareGoosePolicyRight: document.getElementById("compareGoosePolicyRight"),
  compareGoosePolicyButton: document.getElementById("compareGoosePolicyButton"),
  compareGooseCertLeft: document.getElementById("compareGooseCertLeft"),
  compareGooseCertRight: document.getElementById("compareGooseCertRight"),
  compareGooseCertButton: document.getElementById("compareGooseCertButton"),
  compareGooseAdversaryLeft: document.getElementById("compareGooseAdversaryLeft"),
  compareGooseAdversaryRight: document.getElementById("compareGooseAdversaryRight"),
  compareGooseAdversaryButton: document.getElementById("compareGooseAdversaryButton"),
  compareGooseAcpLeft: document.getElementById("compareGooseAcpLeft"),
  compareGooseAcpRight: document.getElementById("compareGooseAcpRight"),
  compareGooseAcpButton: document.getElementById("compareGooseAcpButton"),
  gooseCompareExpandAllButton: document.getElementById("gooseCompareExpandAllButton"),
  gooseCompareCollapseAllButton: document.getElementById("gooseCompareCollapseAllButton"),
  gooseCompareResetFiltersButton: document.getElementById("gooseCompareResetFiltersButton"),
  gooseCompareFilterSummary: document.getElementById("gooseCompareFilterSummary"),
  gooseCompareGroupFilters: document.getElementById("gooseCompareGroupFilters"),
  compareFleetId: document.getElementById("compareFleetId"),
  compareFleetWindowLeft: document.getElementById("compareFleetWindowLeft"),
  compareFleetWindowRight: document.getElementById("compareFleetWindowRight"),
  compareFleetButton: document.getElementById("compareFleetButton"),
  clearDiffButton: document.getElementById("clearDiffButton"),
  reloadReplayButton: document.getElementById("reloadReplayButton"),
  toggleReplayButton: document.getElementById("toggleReplayButton"),
  replayRange: document.getElementById("replayRange"),
  replayAnchorRange: document.getElementById("replayAnchorRange"),
  compareReplayButton: document.getElementById("compareReplayButton"),
  compareNowThenButton: document.getElementById("compareNowThenButton"),
  replayStatus: document.getElementById("replayStatus"),
  timelineCard: document.getElementById("timelineCard"),
  diffCard: document.getElementById("diffCard"),
  operatorCard: document.getElementById("operatorCard"),
  toggleDepthView: document.getElementById("toggleDepthView"),
  depthCanvas: document.getElementById("depthCanvas"),
  depthStatus: document.getElementById("depthStatus"),
  sceneStatus: document.getElementById("sceneStatus"),
  overlayStatus: document.getElementById("overlayStatus"),
  selectionStatus: document.getElementById("selectionStatus"),
};

const state = {
  scene: null,
  overlay: null,
  currentMode: "engineering",
  viewBox: { ...DEFAULT_VIEWBOX },
  selectedNodeId: null,
  drag: null,
  animationHandle: 0,
  replayTimer: 0,
  replay: { frames: [], index: 0, anchorIndex: 0, playing: false, enabled: false },
  filters: {},
  renderTier: "auto",
  activeDiff: null,
  activeDiffTitle: "Diff",
  gooseCompare: {
    domain: null,
    availableGroups: [],
    selectedGroups: [],
    collapseMode: "focus-first",
  },
  performance: {
    reducedMotion: window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches || false,
    frameTimes: [],
    measuredFrameMs: 0,
    autoTier: "balanced",
    lowPower: false,
    pageHidden: document.hidden,
  },
};

function sessionId() {
  const value = localStorage.getItem("nn_session") || crypto.randomUUID();
  localStorage.setItem("nn_session", value);
  return value;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function createSvg(tag, attrs = {}) {
  const element = document.createElementNS(SVG_NS, tag);
  for (const [key, value] of Object.entries(attrs)) {
    element.setAttribute(key, String(value));
  }
  return element;
}

async function fetchJSON(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(await response.text() || response.statusText);
  }
  return response.json();
}

function setSelectOptions(select, values, selectedValue = "") {
  const items = [{ value: "", label: "All" }, ...((values || []).map((entry) => {
    if (entry && typeof entry === "object" && !Array.isArray(entry)) {
      return {
        value: String(entry.value ?? ""),
        label: String(entry.label ?? entry.value ?? ""),
      };
    }
    return {
      value: String(entry ?? ""),
      label: String(entry ?? ""),
    };
  }))];
  select.innerHTML = items
    .map((item) => {
      const selected = String(item.value) === String(selectedValue || "") ? " selected" : "";
      return `<option value="${escapeHtml(item.value)}"${selected}>${escapeHtml(item.label)}</option>`;
    })
    .join("");
}

function parseGoosePolicySelection(value) {
  const [policySetId, version] = String(value || "").split("@@");
  return { policySetId, version };
}

function prettyLabel(value) {
  return String(value || "")
    .replaceAll("_", " ")
    .replaceAll("-", " ")
    .replace(/\s+/g, " ")
    .trim();
}

function summarizeDiffEntries(diff) {
  return Object.entries(diff || {})
    .flatMap(([key, value]) => {
      if (key.endsWith("_changed") && value) {
        return [`${prettyLabel(key.replace(/_changed$/, ""))} changed`];
      }
      if (Array.isArray(value) && value.length) {
        return [`${prettyLabel(key)}: ${value.join(", ")}`];
      }
      if (typeof value === "number" && value !== 0) {
        return [`${prettyLabel(key)}: ${value}`];
      }
      if (value && typeof value === "object" && !Array.isArray(value)) {
        const added = Array.isArray(value.added) ? value.added : [];
        const removed = Array.isArray(value.removed) ? value.removed : [];
        if (added.length || removed.length) {
          return [
            `${prettyLabel(key)}: +${added.join(", ") || "none"} / -${removed.join(", ") || "none"}`,
          ];
        }
      }
      return [];
    })
    .slice(0, 10);
}

function summarizeSceneRefs(sceneDelta) {
  const refs = sceneDelta?.refs || {};
  return Object.entries(refs)
    .map(([key, value]) => `${prettyLabel(key)}=${value}`)
    .slice(0, 8)
    .join(" | ");
}

function gooseCompareDescriptions() {
  return effectiveOverlay()?.diff_catalog?.goose_compare?.group_descriptions || {};
}

function gooseCompareCatalog() {
  return effectiveOverlay()?.diff_catalog?.goose_compare || {};
}

function gooseCompareControlCatalog() {
  return effectiveOverlay()?.inspection_controls?.goose_compare || {};
}

function isGooseCompareDomain(domain) {
  return ["gateway", "policy", "certification", "adversary", "acp"].includes(domain);
}

function gooseCompareGroupCatalog() {
  const controlCatalog = gooseCompareControlCatalog();
  const diffCatalog = gooseCompareCatalog();
  const descriptions = diffCatalog.group_descriptions || {};
  const filters = controlCatalog.group_filters || [];
  if (filters.length) {
    return filters.map((entry) => ({
      value: entry.value,
      label: entry.label || prettyLabel(entry.value),
      description: entry.description || descriptions[entry.value] || "",
    }));
  }
  return (diffCatalog.group_names || []).map((value) => ({
    value,
    label: prettyLabel(value),
    description: descriptions[value] || "",
  }));
}

function syncGooseCompareState({ domain, groups, reset = false }) {
  const availableGroups = (groups || []).map((group) => group.id);
  const defaults = gooseCompareControlCatalog().default_expanded_groups || [];
  if (!isGooseCompareDomain(domain) || !availableGroups.length) {
    state.gooseCompare = {
      domain,
      availableGroups: [],
      selectedGroups: [],
      collapseMode: "focus-first",
    };
    return;
  }
  const previousSelection = new Set(state.gooseCompare.selectedGroups || []);
  const selectedGroups = reset
    ? availableGroups.slice()
    : availableGroups.filter((groupId) => previousSelection.has(groupId));
  state.gooseCompare = {
    domain,
    availableGroups,
    selectedGroups: selectedGroups.length ? selectedGroups : availableGroups.slice(),
    collapseMode: reset
      ? (defaults.length ? "default-expanded" : "focus-first")
      : (state.gooseCompare.collapseMode || "focus-first"),
  };
}

function gooseCompareGroupsForRender(groups) {
  const selected = new Set(state.gooseCompare.selectedGroups || []);
  return (groups || []).filter((group) => selected.has(group.id));
}

function gooseCompareGroupOpen(groupId, index) {
  const defaults = new Set(gooseCompareControlCatalog().default_expanded_groups || []);
  if (state.gooseCompare.collapseMode === "expand-all") {
    return true;
  }
  if (state.gooseCompare.collapseMode === "collapse-all") {
    return false;
  }
  if (state.gooseCompare.collapseMode === "default-expanded" && defaults.size) {
    return defaults.has(groupId);
  }
  return index === 0;
}

function renderGooseCompareControls({ domain, groups }) {
  if (!dom.gooseCompareGroupFilters || !dom.gooseCompareFilterSummary) {
    return;
  }
  const buttons = [
    dom.gooseCompareExpandAllButton,
    dom.gooseCompareCollapseAllButton,
    dom.gooseCompareResetFiltersButton,
  ].filter(Boolean);
  if (!isGooseCompareDomain(domain) || !(groups || []).length) {
    dom.gooseCompareFilterSummary.innerHTML = "<small>Goose filters activate for gateway, policy, certification, adversary, and ACP compare payloads.</small>";
    dom.gooseCompareGroupFilters.innerHTML = "";
    buttons.forEach((button) => {
      button.disabled = true;
    });
    return;
  }
  const availableGroups = new Map((groups || []).map((group) => [group.id, group]));
  const selected = new Set(state.gooseCompare.selectedGroups || []);
  const filterRows = gooseCompareGroupCatalog().map((entry) => {
    const group = availableGroups.get(entry.value);
    const present = Boolean(group);
    const detailCount = group?.items?.length || 0;
    return `
      <label class="inspect-stack">
        <span>
          <input
            type="checkbox"
            data-goose-group-filter="${escapeHtml(entry.value)}"
            ${present && selected.has(entry.value) ? "checked" : ""}
            ${present ? "" : "disabled"}
          >
          <strong>${escapeHtml(entry.label)}</strong>
          <small>${escapeHtml(present ? `${detailCount} deltas` : "not in current diff")}</small>
        </span>
        ${entry.description ? `<small>${escapeHtml(entry.description)}</small>` : ""}
      </label>
    `;
  });
  dom.gooseCompareFilterSummary.innerHTML = `
    <small><strong>Active Goose diff domain:</strong> ${escapeHtml(domain)} | visible-groups=${escapeHtml(String((groups || []).length))} | selected=${escapeHtml(String((state.gooseCompare.selectedGroups || []).length))} | collapse=${escapeHtml(state.gooseCompare.collapseMode || "focus-first")}</small>
  `;
  dom.gooseCompareGroupFilters.innerHTML = filterRows.join("");
  buttons.forEach((button) => {
    button.disabled = false;
  });
}

function rerenderActiveDiffCard() {
  if (!state.activeDiff) {
    renderDiffCard(null, state.activeDiffTitle || "Diff");
    return;
  }
  renderDiffCard(state.activeDiff, state.activeDiffTitle || "Diff");
}

function detectDiffDomain(payload) {
  const left = payload?.left || {};
  if (left.provider_id) {
    return "acp";
  }
  if (left.review_id) {
    return "adversary";
  }
  if (left.stable_certification_id || Object.prototype.hasOwnProperty.call(left, "certification_status")) {
    return "certification";
  }
  if (left.policy_set_id) {
    return "policy";
  }
  if (left.execution_id) {
    return "gateway";
  }
  return "generic";
}

function describeDiffValue(value) {
  if (Array.isArray(value)) {
    return value.length ? value.join(", ") : "none";
  }
  if (typeof value === "boolean") {
    return value ? "yes" : "no";
  }
  if (typeof value === "number") {
    return String(value);
  }
  if (value && typeof value === "object") {
    const added = Array.isArray(value.added) ? value.added : [];
    const removed = Array.isArray(value.removed) ? value.removed : [];
    if (added.length || removed.length) {
      return `+${added.join(", ") || "none"} / -${removed.join(", ") || "none"}`;
    }
    return JSON.stringify(value);
  }
  if (value === null || value === undefined || value === "") {
    return "none";
  }
  return String(value);
}

function groupDefinitionsForDomain(domain) {
  const domains = {
    policy: [
      {
        id: "policy-lifecycle",
        label: "Policy Lifecycle",
        test: (key) => (
          key.includes("status")
          || key.includes("version")
          || key.includes("rollback")
          || key.includes("supersedes")
          || key.includes("lineage")
          || key.includes("bundle_family")
        ),
      },
      {
        id: "permission-deltas",
        label: "Permission Deltas",
        test: (key) => key.includes("permission") || key.includes("allowed_tools") || key.includes("approval_mode"),
      },
      {
        id: "trace-and-artifacts",
        label: "Trace And Artifacts",
        test: (key) => key.includes("linked_report") || key.includes("linked_evidence"),
      },
    ],
    certification: [
      {
        id: "certification-state",
        label: "Certification State",
        test: (key) => (
          key.includes("certification_status")
          || key.includes("policy_status")
          || key.includes("restoration")
          || key.includes("stable_certification")
          || key.includes("lineage")
        ),
      },
      {
        id: "permission-deltas",
        label: "Permission Deltas",
        test: (key) => key.includes("permission") || key.includes("allowed_tools") || key.includes("privilege"),
      },
      {
        id: "adversary-outcome",
        label: "Adversary Outcome",
        test: (key) => key.includes("risk_flags") || key.includes("adversary") || key.includes("remediation"),
      },
      {
        id: "trace-and-artifacts",
        label: "Trace And Artifacts",
        test: (key) => key.includes("artifact") || key.includes("report"),
      },
    ],
    gateway: [
      {
        id: "gateway-execution-path",
        label: "Gateway Execution Path",
        test: (key) => (
          key.includes("execution_kind")
          || key.includes("trigger_source")
          || key.includes("gateway_resolution")
          || key.includes("flow_families")
        ),
      },
      {
        id: "approval-fallback",
        label: "Approval Fallback",
        test: (key) => key.includes("approval") || key.includes("fallback"),
      },
      {
        id: "policy-lifecycle",
        label: "Policy Lifecycle",
        test: (key) => (
          key.includes("extension_bundle")
          || key.includes("extension_policy")
          || key.includes("adversary_report")
          || key.includes("bundle_family")
        ),
      },
      {
        id: "trace-and-artifacts",
        label: "Trace And Artifacts",
        test: (key) => (
          key.includes("linked_trace")
          || key.includes("linked_report")
          || key.includes("artifacts")
          || key.includes("approval_chain_length")
        ),
      },
    ],
    adversary: [
      {
        id: "adversary-outcome",
        label: "Adversary Outcome",
        test: (key) => key.includes("decision") || key.includes("risk_families"),
      },
      {
        id: "permission-deltas",
        label: "Permission Deltas",
        test: (key) => key.includes("requested_tools") || key.includes("requested_extensions"),
      },
      {
        id: "trace-and-artifacts",
        label: "Trace And Artifacts",
        test: (key) => key.includes("report") || key.includes("artifact"),
      },
    ],
    acp: [
      {
        id: "acp-readiness",
        label: "ACP Readiness",
        test: (key) => (
          key.includes("probe")
          || key.includes("version_compatible")
          || key.includes("feature_compatibility")
          || key.includes("status_changed")
        ),
      },
      {
        id: "trace-and-artifacts",
        label: "Trace And Artifacts",
        test: (key) => (
          key.includes("bundle_families")
          || key.includes("compatibility_fixture")
          || key.includes("live_probe_example")
          || key.includes("remediation")
          || key.includes("config_gaps")
        ),
      },
    ],
  };
  return [
    ...(domains[domain] || []),
    {
      id: "trace-and-artifacts",
      label: "Trace And Artifacts",
      test: () => true,
    },
  ];
}

function buildDiffGroups(payload) {
  const diff = payload?.diff || {};
  const sceneDelta = payload?.scene_delta || {};
  const domain = detectDiffDomain(payload);
  const definitions = groupDefinitionsForDomain(domain);
  const descriptions = gooseCompareDescriptions();
  const groups = definitions.map((definition) => ({
    ...definition,
    description: descriptions[definition.id] || definition.description || "",
    items: [],
  }));
  for (const [key, value] of Object.entries(diff)) {
    const target = groups.find((group) => group.test(key, value)) || groups[groups.length - 1];
    target.items.push({
      key,
      label: prettyLabel(key),
      value: describeDiffValue(value),
    });
  }
  if ((sceneDelta.hot_subjects || []).length || (sceneDelta.hot_links || []).length) {
    groups.push({
      id: "scene-delta",
      label: "Scene Delta",
      items: [
        {
          key: "hot_subjects",
          label: "Hot Subjects",
          value: (sceneDelta.hot_subjects || []).map((item) => `${item.subject}:${item.delta > 0 ? "+" : ""}${item.delta}`).join(", ") || "none",
        },
        {
          key: "hot_links",
          label: "Hot Links",
          value: (sceneDelta.hot_links || []).map((item) => `${item.link_id}:${item.delta > 0 ? "+" : ""}${item.delta}`).join(", ") || "none",
        },
      ],
    });
  }
  return groups.filter((group) => group.items.length);
}

function renderDiffGroup(group, open = false) {
  const items = (group.items || [])
    .map((item) => `<div class="kv"><span>${escapeHtml(item.label)}</span><span class="mono">${escapeHtml(item.value)}</span></div>`)
    .join("");
  return `
    <details class="inspect-stack"${open ? " open" : ""}>
      <summary><strong>${escapeHtml(group.label)}</strong> <small>${escapeHtml(String(group.items.length))} deltas</small></summary>
      ${group.description ? `<div class="inspect-row"><small>${escapeHtml(group.description)}</small></div>` : ""}
      <div class="inspect-list">${items}</div>
    </details>
  `;
}

function effectiveOverlay() {
  const live = state.overlay?.overlay_state || {};
  const replayFrame = state.replay.frames?.[state.replay.index];
  if (!replayFrame || !state.replay.enabled) {
    return live;
  }
  return {
    ...live,
    ...(replayFrame.overlay || {}),
    replay_frame_id: replayFrame.frame_id,
  };
}

function effectiveRenderTier() {
  if (state.renderTier !== "auto") {
    return mostConstrainedTier(
      state.renderTier,
      state.performance.lowPower ? "safe" : "full",
      state.performance.pageHidden ? "safe" : "full",
    );
  }
  return mostConstrainedTier(
    state.overlay?.overlay_state?.performance_profile?.recommended_tier || "balanced",
    state.performance.autoTier || "balanced",
    state.performance.reducedMotion ? "safe" : "full",
    state.performance.lowPower ? "safe" : "full",
    state.performance.pageHidden ? "safe" : "full",
  );
}

function tierRank(tier) {
  return { full: 3, balanced: 2, safe: 1 }[tier] || 2;
}

function mostConstrainedTier(...tiers) {
  return [...tiers].reduce((winner, tier) => (tierRank(tier) < tierRank(winner) ? tier : winner), "full");
}

function recordFrameTime(frameMs) {
  const bucket = state.performance.frameTimes;
  bucket.push(frameMs);
  if (bucket.length > 60) {
    bucket.shift();
  }
  const average = bucket.reduce((total, value) => total + value, 0) / Math.max(bucket.length, 1);
  state.performance.measuredFrameMs = Number(average.toFixed(2));
  const currentBudget = state.overlay?.overlay_state?.performance_profile?.frame_budget_ms || {};
  if (state.performance.reducedMotion) {
    state.performance.autoTier = "safe";
    return;
  }
  if (average > (currentBudget.safe || 32) * 1.08) {
    state.performance.autoTier = "safe";
  } else if (average > (currentBudget.balanced || 22) * 1.05) {
    state.performance.autoTier = "balanced";
  } else {
    state.performance.autoTier = "full";
  }
}

function selectedFilters() {
  return {
    registryLayer: dom.filterRegistryLayer.value,
    subject: dom.filterSubject.value,
    teacherPair: dom.filterTeacherPair.value,
    promotionKind: dom.filterPromotionKind.value,
    takeoverStatus: dom.filterTakeoverStatus.value,
    benchmarkFamily: dom.filterBenchmarkFamily.value,
    thresholdSet: dom.filterThresholdSet.value,
    evidenceBundle: dom.filterEvidenceBundle.value,
    disagreement: dom.filterDisagreement.value,
    lineage: dom.filterLineage.value,
    traceWindow: Number(dom.filterTraceWindow.value || 24),
    safePosture: dom.filterSafePosture.value,
  };
}

function currentMode() {
  return state.scene?.modes?.find((mode) => mode.mode_id === state.currentMode) || state.scene?.modes?.[0];
}

function applyModeTheme() {
  const mode = currentMode();
  if (!mode) {
    return;
  }
  document.body.classList.toggle("mode-cinematic", mode.mode_id === "cinematic");
  for (const [key, value] of Object.entries(mode.palette || {})) {
    document.documentElement.style.setProperty(`--${key}`, value);
  }
  dom.modePills.querySelectorAll(".mode-pill").forEach((button) => {
    button.classList.toggle("active", button.dataset.modeId === state.currentMode);
  });
}

function applyViewBox() {
  dom.sceneSvg.setAttribute("viewBox", `${state.viewBox.x} ${state.viewBox.y} ${state.viewBox.w} ${state.viewBox.h}`);
}

function sceneToScreen(x, y) {
  const rect = dom.fxCanvas.getBoundingClientRect();
  const px = ((x - state.viewBox.x) / state.viewBox.w) * rect.width;
  const py = ((y - state.viewBox.y) / state.viewBox.h) * rect.height;
  return { x: px, y: py };
}

function focusNode(nodeId) {
  const node = state.scene?.nodes?.find((candidate) => candidate.node_id === nodeId);
  if (!node) {
    return;
  }
  const target = node.node_type === "core"
    ? { x: node.x - 420, y: node.y - 360, w: 840, h: 720 }
    : { x: node.x - 240, y: node.y - 220, w: 480, h: 440 };
  animateViewBox(target);
  selectNode(nodeId);
}

function animateViewBox(target) {
  const start = { ...state.viewBox };
  const duration = 220;
  const started = performance.now();
  const tick = (now) => {
    const progress = Math.min(1, (now - started) / duration);
    const eased = 1 - Math.pow(1 - progress, 3);
    state.viewBox = {
      x: start.x + (target.x - start.x) * eased,
      y: start.y + (target.y - start.y) * eased,
      w: start.w + (target.w - start.w) * eased,
      h: start.h + (target.h - start.h) * eased,
    };
    applyViewBox();
    if (progress < 1) {
      requestAnimationFrame(tick);
    }
  };
  requestAnimationFrame(tick);
}

function selectNode(nodeId) {
  state.selectedNodeId = nodeId;
  const node = state.scene?.nodes?.find((candidate) => candidate.node_id === nodeId);
  if (!node) {
    return;
  }
  dom.selectionStatus.textContent = `Selected: ${node.label}`;
  renderSelectionCard(node);
  renderDepthInspection();
  renderOperatorCard();
  updateActiveClasses();
}

function renderModePills() {
  dom.modePills.innerHTML = "";
  for (const mode of state.scene.modes || []) {
    const button = document.createElement("button");
    button.className = "mode-pill";
    button.dataset.modeId = mode.mode_id;
    button.textContent = mode.label;
    button.title = mode.description;
    button.addEventListener("click", () => {
      state.currentMode = mode.mode_id;
      applyModeTheme();
      renderLivePosture();
    });
    dom.modePills.appendChild(button);
  }
  applyModeTheme();
}

function renderFilterControls() {
  const overlay = state.overlay?.overlay_state;
  if (!overlay) {
    return;
  }
  const catalog = overlay.filter_catalog || {};
  const defaults = catalog.defaults || {};
  setSelectOptions(dom.filterRegistryLayer, catalog.registry_layers, dom.filterRegistryLayer.value || defaults.registry_layer);
  setSelectOptions(dom.filterSubject, catalog.expert_capsules, dom.filterSubject.value || defaults.expert_capsule);
  setSelectOptions(dom.filterTeacherPair, catalog.teacher_pairs, dom.filterTeacherPair.value);
  setSelectOptions(dom.filterPromotionKind, catalog.promotion_kinds, dom.filterPromotionKind.value);
  setSelectOptions(dom.filterTakeoverStatus, catalog.takeover_statuses, dom.filterTakeoverStatus.value);
  setSelectOptions(dom.filterBenchmarkFamily, catalog.benchmark_families, dom.filterBenchmarkFamily.value);
  setSelectOptions(dom.filterThresholdSet, catalog.threshold_sets, dom.filterThresholdSet.value);
  setSelectOptions(dom.filterEvidenceBundle, catalog.evidence_bundle_ids, dom.filterEvidenceBundle.value);
  setSelectOptions(dom.filterDisagreement, catalog.disagreement_artifact_ids, dom.filterDisagreement.value);
  setSelectOptions(dom.filterLineage, catalog.lineages, dom.filterLineage.value);
  setSelectOptions(dom.filterTraceWindow, catalog.recent_trace_windows, dom.filterTraceWindow.value || defaults.trace_window || 24);
  setSelectOptions(dom.filterSafePosture, catalog.safe_mode_postures, dom.filterSafePosture.value || defaults.safe_mode_posture);

  setSelectOptions(dom.compareBundleLeft, catalog.evidence_bundle_ids, dom.compareBundleLeft.value);
  setSelectOptions(dom.compareBundleRight, catalog.evidence_bundle_ids, dom.compareBundleRight.value);
  setSelectOptions(dom.compareDisagreementLeft, catalog.disagreement_artifact_ids, dom.compareDisagreementLeft.value);
  setSelectOptions(dom.compareDisagreementRight, catalog.disagreement_artifact_ids, dom.compareDisagreementRight.value);
  setSelectOptions(dom.compareReplacementLeft, catalog.replacement_readiness_ids, dom.compareReplacementLeft.value);
  setSelectOptions(dom.compareReplacementRight, catalog.replacement_readiness_ids, dom.compareReplacementRight.value);
  const gooseCompare = overlay.inspection_controls?.goose_compare || {};
  setSelectOptions(dom.compareGooseGatewayLeft, gooseCompare.gateway_executions, dom.compareGooseGatewayLeft.value);
  setSelectOptions(dom.compareGooseGatewayRight, gooseCompare.gateway_executions, dom.compareGooseGatewayRight.value);
  setSelectOptions(dom.compareGoosePolicyLeft, gooseCompare.policy_versions, dom.compareGoosePolicyLeft.value);
  setSelectOptions(dom.compareGoosePolicyRight, gooseCompare.policy_versions, dom.compareGoosePolicyRight.value);
  setSelectOptions(dom.compareGooseCertLeft, gooseCompare.certifications, dom.compareGooseCertLeft.value);
  setSelectOptions(dom.compareGooseCertRight, gooseCompare.certifications, dom.compareGooseCertRight.value);
  setSelectOptions(dom.compareGooseAdversaryLeft, gooseCompare.adversary_reviews, dom.compareGooseAdversaryLeft.value);
  setSelectOptions(dom.compareGooseAdversaryRight, gooseCompare.adversary_reviews, dom.compareGooseAdversaryRight.value);
  setSelectOptions(dom.compareGooseAcpLeft, gooseCompare.acp_providers, dom.compareGooseAcpLeft.value);
  setSelectOptions(dom.compareGooseAcpRight, gooseCompare.acp_providers, dom.compareGooseAcpRight.value);
  setSelectOptions(dom.compareFleetId, overlay.inspection_controls?.available_fleets, dom.compareFleetId.value);
  setSelectOptions(dom.compareFleetWindowLeft, overlay.inspection_controls?.available_windows, dom.compareFleetWindowLeft.value || "short");
  setSelectOptions(dom.compareFleetWindowRight, overlay.inspection_controls?.available_windows, dom.compareFleetWindowRight.value || "long");
}

function renderLegend() {
  const legend = state.scene?.legend || {};
  const items = [];
  for (const group of ["node_types", "link_types", "loops", "overlays"]) {
    for (const item of legend[group] || []) {
      items.push(`
        <div class="legend-item">
          <span class="legend-swatch" style="color:${legendColor(item.id)}"></span>
          <div>
            <strong>${escapeHtml(item.label)}</strong>
            <div class="mono">${escapeHtml(item.id)}</div>
          </div>
        </div>
      `);
    }
  }
  dom.legend.innerHTML = items.join("");
}

function legendColor(id) {
  const map = {
    core: "var(--core)",
    capsule: "var(--capsule)",
    subnode: "rgba(255,255,255,0.82)",
    collaboration: "var(--capsule)",
    critique: "var(--critique)",
    dream: "var(--dream)",
    consequence: "var(--consequence)",
    promotion: "var(--warning)",
    takeover: "var(--safe)",
    physiology: "var(--warning)",
  };
  return map[id] || "var(--muted)";
}

function renderGrid() {
  dom.gridLayer.innerHTML = "";
  for (const radius of [320, 520, 760, 980]) {
    dom.gridLayer.appendChild(createSvg("circle", {
      cx: 0,
      cy: 0,
      r: radius,
      fill: "none",
      stroke: "rgba(154, 167, 194, 0.08)",
      "stroke-width": 1,
    }));
  }
  for (let index = 0; index < 12; index += 1) {
    const angle = (Math.PI * 2 * index) / 12;
    dom.gridLayer.appendChild(createSvg("line", {
      x1: Math.cos(angle) * 120,
      y1: Math.sin(angle) * 120,
      x2: Math.cos(angle) * 980,
      y2: Math.sin(angle) * 980,
      stroke: "rgba(154, 167, 194, 0.05)",
      "stroke-width": 1,
    }));
  }
}

function curvePath(source, target, bend = 0.12) {
  const mx = (source.x + target.x) / 2;
  const my = (source.y + target.y) / 2;
  const dx = target.x - source.x;
  const dy = target.y - source.y;
  const cx = mx - dy * bend;
  const cy = my + dx * bend;
  return `M ${source.x} ${source.y} Q ${cx} ${cy} ${target.x} ${target.y}`;
}

function distanceBetween(left, right) {
  return Math.hypot((left.x || 0) - (right.x || 0), (left.y || 0) - (right.y || 0));
}

function buildMeshSegments(node) {
  const points = node.internal_nodes || [];
  const threshold = node.node_type === "core" ? 112 : 58;
  const segments = [];
  const seen = new Set();
  for (const point of points) {
    const neighbors = points
      .filter((candidate) => candidate.id !== point.id)
      .map((candidate) => ({ candidate, distance: distanceBetween(point, candidate) }))
      .filter((entry) => entry.distance <= threshold)
      .sort((left, right) => left.distance - right.distance)
      .slice(0, node.node_type === "core" ? 3 : 2);
    for (const { candidate, distance } of neighbors) {
      const pairId = [point.id, candidate.id].sort().join("::");
      if (seen.has(pairId)) {
        continue;
      }
      seen.add(pairId);
      segments.push({
        source: point,
        target: candidate,
        distance,
      });
    }
  }
  return segments.slice(0, node.node_type === "core" ? 96 : 42);
}

function portPositions(node) {
  const motifCount = Math.max(3, Math.min(8, (node.meta?.motif_labels || []).length || 4));
  const shellRadius = (node.radius || (node.node_type === "core" ? 214 : 96)) + (node.node_type === "core" ? 16 : 10);
  return Array.from({ length: motifCount }, (_, index) => {
    const angle = (-Math.PI / 2) + ((Math.PI * 2 * index) / motifCount);
    return {
      x: Math.cos(angle) * shellRadius,
      y: Math.sin(angle) * shellRadius,
    };
  });
}

function renderLinks() {
  dom.linkLayer.innerHTML = "";
  const nodeIndex = new Map((state.scene?.nodes || []).map((node) => [node.node_id, node]));
  for (const link of state.scene?.links || []) {
    const source = nodeIndex.get(link.source_id);
    const target = nodeIndex.get(link.target_id);
    if (!source || !target) {
      continue;
    }
    const path = createSvg("path", {
      d: curvePath(source, target, link.link_type === "core" ? 0.05 : 0.1),
      class: `scene-link ${link.link_type}`,
      "data-link-id": link.link_id,
      "data-source-id": link.source_id,
      "data-target-id": link.target_id,
    });
    dom.linkLayer.appendChild(path);
  }
}

function renderLoops() {
  dom.loopLayer.innerHTML = "";
  const loopVisibility = {
    dream: dom.toggleDream.checked,
    critique: dom.toggleCritique.checked,
    consequence: dom.toggleConsequence.checked,
  };
  for (const loop of state.scene?.loops || []) {
    const ellipse = createSvg("ellipse", {
      cx: 0,
      cy: 0,
      rx: loop.orbit_radius * 1.55,
      ry: loop.orbit_radius,
      class: `scene-loop ${loop.loop_type}${loopVisibility[loop.loop_type] ? "" : " hidden"}`,
      "data-loop-id": loop.loop_id,
    });
    dom.loopLayer.appendChild(ellipse);
  }
}

function renderNodes() {
  dom.nodeLayer.innerHTML = "";
  for (const node of state.scene?.nodes || []) {
    const group = createSvg("g", {
      class: `node-group ${node.node_type} ${node.subject ? `subject-${node.subject}` : ""}`,
      transform: `translate(${node.x} ${node.y})`,
      "data-node-id": node.node_id,
      "data-subject": node.subject || "",
    });
    group.addEventListener("click", (event) => {
      event.stopPropagation();
      focusNode(node.node_id);
    });

    const shell = createSvg("circle", {
      class: "node-shell",
      cx: 0,
      cy: 0,
      r: node.radius || (node.node_type === "core" ? 214 : 96),
    });
    group.appendChild(shell);

    if (node.node_type === "core") {
      for (const radius of node.meta.ring_radii || []) {
        group.appendChild(createSvg("circle", { class: "node-ring", cx: 0, cy: 0, r: radius }));
      }
    } else {
      for (const radius of [node.radius * 0.64, node.radius * 0.82]) {
        group.appendChild(createSvg("circle", { class: "node-ring", cx: 0, cy: 0, r: radius }));
      }
    }

    for (const segment of buildMeshSegments(node)) {
      group.appendChild(createSvg("line", {
        class: "inner-link",
        x1: segment.source.x,
        y1: segment.source.y,
        x2: segment.target.x,
        y2: segment.target.y,
      }));
    }

    for (const internalNode of node.internal_nodes || []) {
      group.appendChild(createSvg("circle", {
        class: "inner-node",
        cx: internalNode.x,
        cy: internalNode.y,
        r: node.node_type === "core" ? 4.2 : 3.4,
      }));
    }

    for (const port of portPositions(node)) {
      group.appendChild(createSvg("circle", {
        class: "port-node",
        cx: port.x,
        cy: port.y,
        r: node.node_type === "core" ? 4.6 : 3.4,
      }));
    }

    group.appendChild(createSvg("text", { class: "node-title", x: 0, y: node.node_type === "core" ? -10 : -4 }));
    group.lastChild.textContent = node.node_type === "core" ? "NexusNet" : node.label.replace(" Expert", "");

    const subtitle = createSvg("text", { class: "node-subtitle", x: 0, y: node.node_type === "core" ? 18 : 18 });
    subtitle.textContent = node.node_type === "core" ? "Brain Core" : (node.subject || "").replaceAll("-", " ");
    group.appendChild(subtitle);

    dom.nodeLayer.appendChild(group);
  }
  updateActiveClasses();
}

function updateActiveClasses() {
  const overlay = effectiveOverlay();
  const activeSubjects = new Set(overlay.active_subjects || []);
  const selectedTeachers = overlay.selected_teachers || {};
  const critiqueArbitrating = Boolean(overlay.arbitration_result);
  const linkActivity = overlay.link_activity?.edges || {};
  const coreToCapsule = overlay.link_activity?.core_to_capsule || {};
  const diffSubjects = new Map((state.activeDiff?.scene_delta?.hot_subjects || []).map((item) => [item.subject, item.delta]));
  const diffLinks = new Map((state.activeDiff?.scene_delta?.hot_links || []).map((item) => [item.link_id, item.delta]));
  const filters = selectedFilters();
  const currentTeacherPair = [selectedTeachers.primary, selectedTeachers.secondary].filter(Boolean).join("::");
  const currentBenchmarkFamily = (overlay.benchmark_refs || [])[0] || "";
  const currentLineage = state.replay.enabled
    ? (state.replay.frames?.[state.replay.index]?.lineage || "")
    : (overlay.dream_activity?.dream_lineage || "live-derived");
  const currentSafePosture = overlay.safe_mode_physiology?.safe_mode
    ? "contracted"
    : (overlay.safe_mode_physiology?.retry_state || "stable");
  const globalFilterMismatch =
    (filters.teacherPair && currentTeacherPair !== filters.teacherPair) ||
    (filters.benchmarkFamily && currentBenchmarkFamily !== filters.benchmarkFamily) ||
    (filters.lineage && currentLineage !== filters.lineage) ||
    (filters.safePosture && currentSafePosture !== filters.safePosture);

  dom.nodeLayer.querySelectorAll(".node-group").forEach((group) => {
    group.classList.remove("active", "selected", "dimmed", "filtered-out", "telemetry-hot", "compare-left", "compare-right", "compare-delta-positive", "compare-delta-negative");
    const nodeId = group.dataset.nodeId;
    const subject = group.dataset.subject;
    const intensity = subject ? (coreToCapsule[subject]?.intensity || 0) : 1;
    group.style.setProperty("--node-intensity", String(intensity));
    if (nodeId === state.selectedNodeId) {
      group.classList.add("selected");
    }
    if ((subject && activeSubjects.has(subject)) || (subject === "critique" && critiqueArbitrating)) {
      group.classList.add("active");
    }
    if (intensity >= 0.28) {
      group.classList.add("telemetry-hot");
    }
    const shouldDim = activeSubjects.size > 0 && subject && !activeSubjects.has(subject) && subject !== "critique";
    if (shouldDim) {
      group.classList.add("dimmed");
    }
    if (Object.values(selectedTeachers).includes(subject)) {
      group.classList.add("active");
    }
    if (subject && diffSubjects.has(subject)) {
      const delta = diffSubjects.get(subject) || 0;
      if (delta > 0) {
        group.classList.add("compare-right", "compare-delta-positive");
      } else if (delta < 0) {
        group.classList.add("compare-left", "compare-delta-negative");
      }
    }
    const filteredOut =
      globalFilterMismatch ||
      (filters.subject && subject && filters.subject !== subject) ||
      (filters.registryLayer && overlay.active_registry_layer && overlay.active_registry_layer !== filters.registryLayer);
    if (filteredOut) {
      group.classList.add("filtered-out");
    }
  });

  dom.linkLayer.querySelectorAll(".scene-link").forEach((path) => {
    path.classList.remove("active", "compare-hot", "compare-up", "compare-down");
    const linkId = path.dataset.linkId || "";
    const source = path.dataset.sourceId || "";
    const target = path.dataset.targetId || "";
    const intensity = linkActivity[linkId]?.intensity || 0;
    path.style.setProperty("--link-intensity", String(intensity));
    if ([source, target].includes(state.selectedNodeId)) {
      path.classList.add("active");
    }
    if (intensity >= 0.22) {
      path.classList.add("active");
    }
    if (diffLinks.has(linkId)) {
      const delta = diffLinks.get(linkId) || 0;
      path.classList.add("compare-hot");
      path.style.setProperty("--compare-delta", String(Math.abs(delta)));
      path.style.setProperty("--compare-delta-abs", String(Math.abs(delta)));
      path.classList.add(delta >= 0 ? "compare-up" : "compare-down");
    }
  });

  dom.loopLayer.querySelectorAll(".scene-loop").forEach((ellipse) => {
    const loopId = ellipse.dataset.loopId || "";
    const loopType = loopId.includes("dream") ? "dream" : loopId.includes("critique") ? "critique" : "consequence";
    const intensity = overlay.loop_activity?.[loopType]?.intensity || 0.18;
    ellipse.style.setProperty("--loop-intensity", String(intensity));
  });

  renderOverlayAnnotations(overlay);
}

function renderOverlayAnnotations(overlay) {
  dom.overlayLayer.innerHTML = "";
  if (!state.scene || !overlay) {
    return;
  }
  const hotSubjects = (state.activeDiff?.scene_delta?.hot_subjects || []).slice(0, 6);
  const hotLinks = (state.activeDiff?.scene_delta?.hot_links || []).slice(0, 6);
  const nodeIndex = new Map((state.scene.nodes || []).map((node) => [node.node_id, node]));

  hotSubjects.forEach((item, index) => {
    const node = state.scene.nodes.find((candidate) => candidate.subject === item.subject);
    if (!node) {
      return;
    }
    const badge = createSvg("g", {
      class: `overlay-annotation subject-delta ${item.delta >= 0 ? "positive" : "negative"}`,
      transform: `translate(${node.x} ${node.y - ((node.radius || 96) + 38 + index * 6)})`,
    });
    badge.appendChild(createSvg("rect", { class: "overlay-pill", x: -68, y: -16, rx: 16, ry: 16, width: 136, height: 32 }));
    const label = createSvg("text", { class: "overlay-badge", x: 0, y: 5 });
    label.textContent = `${item.subject} ${item.delta > 0 ? "+" : ""}${item.delta}`;
    badge.appendChild(label);
    dom.overlayLayer.appendChild(badge);
  });

  hotLinks.forEach((item, index) => {
    const link = state.scene.links.find((candidate) => candidate.link_id === item.link_id);
    const source = link ? nodeIndex.get(link.source_id) : null;
    const target = link ? nodeIndex.get(link.target_id) : null;
    if (!source || !target) {
      return;
    }
    const mx = (source.x + target.x) / 2;
    const my = (source.y + target.y) / 2;
    const badge = createSvg("g", {
      class: `overlay-annotation link-delta ${item.delta >= 0 ? "positive" : "negative"}`,
      transform: `translate(${mx} ${my - (18 + index * 5)})`,
    });
    badge.appendChild(createSvg("rect", { class: "overlay-pill compact", x: -60, y: -13, rx: 13, ry: 13, width: 120, height: 26 }));
    const label = createSvg("text", { class: "overlay-badge compact", x: 0, y: 4 });
    label.textContent = `${item.link_id} ${item.delta > 0 ? "+" : ""}${item.delta}`;
    badge.appendChild(label);
    dom.overlayLayer.appendChild(badge);
  });

  const core = state.scene.nodes.find((node) => node.node_type === "core");
  const physiology = overlay.safe_mode_physiology || {};
  if (core && dom.togglePhysiology.checked) {
    const flags = [
      physiology.safe_mode ? "SAFE CONTRACTED" : null,
      physiology.thermal_mode && physiology.thermal_mode !== "unknown" ? `THERMAL ${physiology.thermal_mode}` : null,
      physiology.vram_pressure && !["unknown", "unreported", ""].includes(physiology.vram_pressure) ? `VRAM ${physiology.vram_pressure}` : null,
      physiology.retry_state && physiology.retry_state !== "stable" ? `RETRY ${physiology.retry_state}` : null,
    ].filter(Boolean);
    if (flags.length) {
      const posture = createSvg("g", {
        class: "overlay-annotation physiology-summary positive",
        transform: `translate(${core.x} ${core.y + 286})`,
      });
      posture.appendChild(createSvg("rect", { class: "overlay-pill wide", x: -188, y: -18, rx: 18, ry: 18, width: 376, height: 36 }));
      const label = createSvg("text", { class: "overlay-badge", x: 0, y: 6 });
      label.textContent = flags.join(" | ");
      posture.appendChild(label);
      dom.overlayLayer.appendChild(posture);
    }
  }
}

function renderSelectionCard(node) {
  const overlay = effectiveOverlay();
  const motifList = (node.meta?.motif_labels || []).map((motif) => `<span class="mono">${escapeHtml(motif)}</span>`).join(", ") || "canonical topology";
  const internalCount = (node.internal_nodes || []).length;
  const layerCounts = Object.entries(
    (node.internal_nodes || []).reduce((accumulator, item) => {
      const key = String(item.layer_index ?? "mesh");
      accumulator[key] = (accumulator[key] || 0) + 1;
      return accumulator;
    }, {}),
  )
    .map(([layer, count]) => `${layer}:${count}`)
    .join(" | ") || "mesh";
  const kindCounts = Object.entries(
    (node.internal_nodes || []).reduce((accumulator, item) => {
      const key = String(item.kind || "node");
      accumulator[key] = (accumulator[key] || 0) + 1;
      return accumulator;
    }, {}),
  )
    .map(([kind, count]) => `${kind}:${count}`)
    .slice(0, 5)
    .join(" | ") || "neural-cluster";
  const portCount = portPositions(node).length;
  const teacherRefs = (overlay.teacher_evidence_refs?.bundle_ids || []).slice(0, 3).map(escapeHtml).join(", ") || "none";
  const foundryRefs = (overlay.foundry_evidence_refs?.fleet_summary_ids || []).slice(0, 3).map(escapeHtml).join(", ") || "none";
  const clusterKinds = [...new Set((node.internal_nodes || []).map((item) => item.kind))].slice(0, 6).map(escapeHtml).join(", ") || "neural-cluster";
  dom.selectionCard.innerHTML = `
    <div class="inspect-row">
      <strong>${escapeHtml(node.label)}</strong>
      <small>${escapeHtml(node.node_type.toUpperCase())}</small>
    </div>
    <div class="inspect-list">
      <div class="kv"><span>Node ID</span><span class="mono">${escapeHtml(node.node_id)}</span></div>
      <div class="kv"><span>Subject</span><span>${escapeHtml(node.subject || "core-brain")}</span></div>
      <div class="kv"><span>Topology</span><span class="mono">${escapeHtml(node.topology_id || "nexus-core")}</span></div>
      <div class="kv"><span>Internal nodes</span><span>${internalCount}</span></div>
      <div class="kv"><span>Port anchors</span><span>${portCount}</span></div>
      <div class="kv"><span>Cluster motifs</span><span>${escapeHtml(clusterKinds)}</span></div>
      <div class="kv"><span>Status</span><span>${escapeHtml(node.status_label)}</span></div>
    </div>
    <div class="inspect-row">
      <small>${escapeHtml(node.meta?.description || "Canonical neural structure.")}</small>
    </div>
    <div class="inspect-row">
      <small><strong>Motifs:</strong> ${motifList}</small>
    </div>
    <div class="inspect-row">
      <small><strong>Layers:</strong> ${escapeHtml(layerCounts)}</small>
    </div>
    <div class="inspect-row">
      <small><strong>Cluster density:</strong> ${escapeHtml(kindCounts)}</small>
    </div>
    <div class="inspect-row">
      <small><strong>Teacher refs:</strong> ${teacherRefs}</small>
    </div>
    <div class="inspect-row">
      <small><strong>Foundry refs:</strong> ${foundryRefs}</small>
    </div>
  `;
}

function renderLivePosture() {
  const overlay = effectiveOverlay();
  if (!overlay) {
    dom.livePosture.innerHTML = "No live posture loaded.";
    return;
  }
  const runtime = overlay.runtime_posture || {};
  const physiology = overlay.safe_mode_physiology || {};
  const physiologyActivity = overlay.physiology_activity || {};
  const performanceProfile = overlay.performance_profile || {};
  dom.livePosture.innerHTML = `
    <div class="metric"><strong>${escapeHtml(overlay.active_registry_layer || "pending")}</strong><small>Registry Layer</small></div>
    <div class="metric"><strong>${escapeHtml(runtime.selected_runtime_name || "pending")}</strong><small>Runtime</small></div>
    <div class="metric"><strong>${escapeHtml(runtime.selected_backend_name || "pending")}</strong><small>Backend</small></div>
    <div class="metric"><strong>${escapeHtml(physiology.thermal_mode || "unknown")}</strong><small>Thermal Mode</small></div>
    <div class="metric"><strong>${escapeHtml(physiology.vram_pressure || "unreported")}</strong><small>VRAM Pressure</small></div>
    <div class="metric"><strong>${escapeHtml(physiology.retry_state || "stable")}</strong><small>Retry State</small></div>
    <div class="metric"><strong>${escapeHtml(String(overlay.active_subjects?.length || 0))}</strong><small>Active Capsules</small></div>
    <div class="metric"><strong>${escapeHtml(performanceProfile.recommended_tier || "balanced")}</strong><small>Render Tier</small></div>
    <div class="metric"><strong>${escapeHtml(String((physiologyActivity.degraded_channels || []).length))}</strong><small>Degraded Channels</small></div>
  `;

  document.body.classList.toggle("physiology-safe", Boolean(physiology.safe_mode) && dom.togglePhysiology.checked);
  document.body.classList.toggle("physiology-thermal", physiology.thermal_mode && physiology.thermal_mode !== "unknown" && dom.togglePhysiology.checked);
  document.body.classList.toggle("physiology-retry", physiology.retry_state !== "stable" && dom.togglePhysiology.checked);
  document.body.classList.toggle("render-full", effectiveRenderTier() === "full");
  document.body.classList.toggle("render-balanced", effectiveRenderTier() === "balanced");
  document.body.classList.toggle("render-safe", effectiveRenderTier() === "safe");
  document.body.classList.toggle("low-power", state.performance.lowPower);
  document.body.classList.toggle("page-hidden", state.performance.pageHidden);
}

function renderEvidenceCards() {
  const overlay = effectiveOverlay();
  if (!overlay) {
    return;
  }
  const evidenceActivity = overlay.evidence_activity || {};
  const filters = selectedFilters();
  const filterSummary = Object.entries(filters)
    .filter(([, value]) => value !== "" && value !== 0 && value !== null && value !== undefined && !(typeof value === "number" && Number.isNaN(value)))
    .map(([key, value]) => `${key}=${value}`)
    .slice(0, 5)
    .join(" | ");
  dom.evidenceCard.innerHTML = `
    <div class="inspect-list">
      <div class="kv"><span>Primary</span><span class="mono">${escapeHtml(overlay.selected_teachers?.primary || "none")}</span></div>
      <div class="kv"><span>Secondary</span><span class="mono">${escapeHtml(overlay.selected_teachers?.secondary || "none")}</span></div>
      <div class="kv"><span>Critique</span><span class="mono">${escapeHtml(overlay.selected_teachers?.critique || "none")}</span></div>
      <div class="kv"><span>Arbitration</span><span>${escapeHtml(overlay.arbitration_result || "unbound")}</span></div>
      <div class="kv"><span>Teacher intensity</span><span>${escapeHtml(String(evidenceActivity.teacher?.intensity ?? 0))}</span></div>
      <div class="kv"><span>Rerank evidence</span><span class="mono">${escapeHtml(overlay.route_activity?.rerank_promotion_evidence_ref || "none")}</span></div>
    </div>
    <div class="inspect-row"><small><strong>Benchmark refs:</strong> ${(overlay.benchmark_refs || []).map(escapeHtml).join(", ") || "none"}</small></div>
    <div class="inspect-row"><small><strong>Threshold refs:</strong> ${(overlay.threshold_refs || []).map(escapeHtml).join(", ") || "none"}</small></div>
    <div class="inspect-row"><small><strong>Rerank review:</strong> ${escapeHtml(overlay.route_activity?.rerank_review_report_id || "none")} | threshold=${escapeHtml(overlay.route_activity?.rerank_threshold_set_id || "none")}</small></div>
    <div class="inspect-row"><small><strong>Rerank headline:</strong> ${escapeHtml(overlay.route_activity?.rerank_review_headline || "none")}</small></div>
    <div class="inspect-row"><small><strong>Rerank summary:</strong> ${escapeHtml(overlay.route_activity?.rerank_review_human_summary || "none")}</small></div>
    <div class="inspect-row"><small><strong>Rerank shifts:</strong> changed=${escapeHtml(String(overlay.route_activity?.rerank_candidate_shift_count || 0))} | top=${escapeHtml(overlay.route_activity?.rerank_top_shift_chunk_id || "none")} | delta=${escapeHtml(String(overlay.route_activity?.rerank_top_shift_delta ?? "none"))}</small></div>
    <div class="inspect-row"><small><strong>Evidence bundles:</strong> ${(overlay.teacher_evidence_refs?.bundle_ids || []).slice(0, 4).map(escapeHtml).join(", ") || "none"}</small></div>
    <div class="inspect-row"><small><strong>Disagreements:</strong> ${(overlay.teacher_evidence_refs?.disagreement_ids || []).slice(0, 4).map(escapeHtml).join(", ") || "none"}</small></div>
    <div class="inspect-row"><small><strong>Filter context:</strong> ${escapeHtml(filterSummary || "none")}</small></div>
  `;

  dom.governanceCard.innerHTML = `
    <div class="inspect-list">
      <div class="kv"><span>Promotion candidates</span><span>${escapeHtml(String(overlay.promotion_cues?.candidate_count || 0))}</span></div>
      <div class="kv"><span>Native takeovers</span><span>${escapeHtml(String(overlay.takeover_cues?.native_takeover_count || 0))}</span></div>
      <div class="kv"><span>Dream-derived traces</span><span>${escapeHtml(String(overlay.dream_activity?.recent_dream_derived_count || 0))}</span></div>
      <div class="kv"><span>Telemetry horizon</span><span class="mono">${escapeHtml(overlay.telemetry_window?.horizon || "recent-0")}</span></div>
      <div class="kv"><span>Replay frame</span><span class="mono">${escapeHtml(state.replay.frames?.[state.replay.index]?.frame_id || "live")}</span></div>
      <div class="kv"><span>Rerank scorecard</span><span class="mono">${escapeHtml(overlay.route_activity?.rerank_scorecard_ref || "none")}</span></div>
    </div>
    <div class="inspect-row"><small><strong>Rerank deltas:</strong> passed=${escapeHtml(String(overlay.route_activity?.rerank_scorecard_passed ?? false))} | provider=${escapeHtml(overlay.route_activity?.rerank_provider_badge || "none")} | eval-artifacts=${escapeHtml(String(overlay.route_activity?.rerank_evaluator_artifact_count || 0))}</small></div>
    <div class="inspect-row"><small><strong>Rerank review refs:</strong> review=${escapeHtml(overlay.route_activity?.rerank_review_report_id || "none")} | artifact=${escapeHtml(overlay.route_activity?.rerank_review_artifact_ref || "none")}</small></div>
    <div class="inspect-row"><small><strong>Replacement readiness:</strong> ${(overlay.takeover_cues?.replacement_readiness_ids || []).slice(0, 4).map(escapeHtml).join(", ") || "none"}</small></div>
    <div class="inspect-row"><small><strong>Cohort / fleet refs:</strong> ${(overlay.foundry_evidence_refs?.fleet_summary_ids || []).slice(0, 4).map(escapeHtml).join(", ") || "none"}</small></div>
    <div class="inspect-row"><small><strong>Retirement shadow:</strong> ${(overlay.foundry_evidence_refs?.retirement_shadow_ids || []).slice(0, 4).map(escapeHtml).join(", ") || "none"}</small></div>
    <div class="inspect-row"><small><strong>Active diff refs:</strong> ${escapeHtml(state.activeDiff?.scene_delta?.refs?.left || state.activeDiff?.scene_delta?.refs?.fleet_id || "none")} -> ${escapeHtml(state.activeDiff?.scene_delta?.refs?.right || "none")}</small></div>
  `;
}

function renderOperatorCard() {
  const overlay = effectiveOverlay();
  if (!overlay) {
    dom.operatorCard.innerHTML = "Operator inspection unavailable.";
    return;
  }
  const providers = overlay.telemetry_sources?.providers || [];
  const logChannels = overlay.telemetry_sources?.log_channels || {};
  const providerSummary = overlay.telemetry_sources?.summary || {};
  const performanceProfile = overlay.performance_profile || {};
  const currentFrame = state.replay.frames?.[state.replay.index];
  const gooseCompareCatalog = overlay.diff_catalog?.goose_compare || {};
  dom.operatorCard.innerHTML = `
    <div class="inspect-grid">
      <div class="inspect-row">
        <strong>${escapeHtml(effectiveRenderTier())}</strong>
        <small>Effective Render Tier</small>
      </div>
      <div class="inspect-row">
        <strong>${escapeHtml(String(state.performance.measuredFrameMs || 0))} ms</strong>
        <small>Measured Frame Avg</small>
      </div>
      <div class="inspect-row">
        <strong>${escapeHtml(String((overlay.physiology_activity?.degraded_channels || []).length))}</strong>
        <small>Degraded Channels</small>
      </div>
      <div class="inspect-row">
        <strong>${escapeHtml(String(providers.filter((provider) => provider.bound).length))}/${escapeHtml(String(providers.length))}</strong>
        <small>Telemetry Providers Bound</small>
      </div>
      <div class="inspect-row">
        <strong>${escapeHtml(providerSummary.health || "degraded")}</strong>
        <small>Provider Health</small>
      </div>
      <div class="inspect-row">
        <strong>${escapeHtml(state.performance.lowPower ? "clamped" : "normal")}</strong>
        <small>Low Power</small>
      </div>
    </div>
    <div class="inspect-row"><small><strong>Providers:</strong> ${providers.map((provider) => `${escapeHtml(provider.provider_id)}:${provider.bound ? "bound" : "degraded"}:${escapeHtml(provider.kind || "unknown")}:${escapeHtml(String(provider.signal_count || 0))}`).join(" | ") || "none"}</small></div>
    <div class="inspect-row"><small><strong>Log channels:</strong> ${Object.entries(logChannels).map(([name, channel]) => `${escapeHtml(name)}=${escapeHtml(String(channel.count || 0))}`).join(" | ") || "none"}</small></div>
    <div class="inspect-row"><small><strong>Replay frame:</strong> ${escapeHtml(currentFrame?.frame_id || "live")} | ${escapeHtml(currentFrame?.source_ref?.provider_chain?.join(" -> ") || "live-wrapper-state")}</small></div>
    <div class="inspect-row"><small><strong>Depth mode:</strong> ${escapeHtml(performanceProfile.depth_mode?.renderer || "svg-canvas")} | ${performanceProfile.depth_mode?.allowed ? "allowed" : "disabled"}</small></div>
    <div class="inspect-row"><small><strong>Source health:</strong> signals=${escapeHtml(String(providerSummary.signal_count || 0))} | latest=${escapeHtml(providerSummary.latest_trace_id || "none")} | bound-ratio=${escapeHtml(String(providerSummary.bound_ratio || 0))}</small></div>
    <div class="inspect-row"><small><strong>Replay source metadata:</strong> ${escapeHtml(currentFrame?.created_at || "live-now")} | ${escapeHtml(currentFrame?.selected_expert || overlay.route_activity?.selected_expert || "idle")} | hidden=${escapeHtml(String(state.performance.pageHidden))}</small></div>
    <div class="inspect-row"><small><strong>OpenJarvis doctor:</strong> preset=${escapeHtml(overlay.runtime_posture?.openjarvis_recommended_preset || "none")} | runtime=${escapeHtml(overlay.runtime_posture?.openjarvis_recommended_runtime || "none")} | skills=${escapeHtml(String(overlay.runtime_posture?.openjarvis_skill_catalog_count || 0))} | scheduled=${escapeHtml(String(overlay.runtime_posture?.openjarvis_scheduled_workflow_count || 0))}</small></div>
    <div class="inspect-row"><small><strong>OpenJarvis eval dims:</strong> energy_wh=${escapeHtml(String(overlay.runtime_posture?.openjarvis_cost_energy_wh ?? 0))} | edge-provider=${escapeHtml(overlay.runtime_posture?.edge_vision_default_provider || "none")} | edge-cases=${escapeHtml(String(overlay.runtime_posture?.edge_vision_benchmark_case_count || 0))}</small></div>
    <div class="inspect-row"><small><strong>Goose recipes:</strong> recipes=${escapeHtml(String(overlay.runtime_posture?.goose_recipe_count || 0))} | runbooks=${escapeHtml(String(overlay.runtime_posture?.goose_runbook_count || 0))} | schedule-compatible=${escapeHtml(String(overlay.runtime_posture?.goose_schedule_compatible_count || 0))}</small></div>
    <div class="inspect-row"><small><strong>Goose history:</strong> recipe-execs=${escapeHtml(String(overlay.runtime_posture?.goose_recipe_execution_count || 0))} | latest-recipe=${escapeHtml(overlay.runtime_posture?.goose_latest_recipe_execution_id || "none")} | recipe-report=${escapeHtml(overlay.runtime_posture?.goose_latest_recipe_report_id || "none")} | recipe-gateway=${escapeHtml(overlay.runtime_posture?.goose_latest_recipe_gateway_resolution_id || "none")} | gateway-exec=${escapeHtml(overlay.runtime_posture?.goose_latest_recipe_gateway_execution_id || "none")} | gateway-report=${escapeHtml(overlay.runtime_posture?.goose_latest_recipe_gateway_report_id || "none")} | recipe-adv=${escapeHtml(overlay.runtime_posture?.goose_latest_recipe_adversary_report_id || "none")} | trace=${escapeHtml(overlay.runtime_posture?.goose_latest_recipe_linked_trace_id || "none")} | report-link=${escapeHtml(overlay.runtime_posture?.goose_latest_recipe_linked_report_id || "none")} | families=${escapeHtml(JSON.stringify(overlay.runtime_posture?.goose_recipe_flow_family_counts || {}))}</small></div>
    <div class="inspect-row"><small><strong>Goose runbooks:</strong> runbook-execs=${escapeHtml(String(overlay.runtime_posture?.goose_runbook_execution_count || 0))} | latest-runbook=${escapeHtml(overlay.runtime_posture?.goose_latest_runbook_execution_id || "none")} | runbook-report=${escapeHtml(overlay.runtime_posture?.goose_latest_runbook_report_id || "none")} | runbook-gateway=${escapeHtml(overlay.runtime_posture?.goose_latest_runbook_gateway_resolution_id || "none")} | gateway-exec=${escapeHtml(overlay.runtime_posture?.goose_latest_runbook_gateway_execution_id || "none")} | gateway-report=${escapeHtml(overlay.runtime_posture?.goose_latest_runbook_gateway_report_id || "none")} | runbook-adv=${escapeHtml(overlay.runtime_posture?.goose_latest_runbook_adversary_report_id || "none")} | trace=${escapeHtml(overlay.runtime_posture?.goose_latest_runbook_linked_trace_id || "none")} | report-link=${escapeHtml(overlay.runtime_posture?.goose_latest_runbook_linked_report_id || "none")} | families=${escapeHtml(JSON.stringify(overlay.runtime_posture?.goose_runbook_flow_family_counts || {}))}</small></div>
    <div class="inspect-row"><small><strong>Goose gateway:</strong> execs=${escapeHtml(String(overlay.runtime_posture?.goose_gateway_execution_count || 0))} | latest=${escapeHtml(overlay.runtime_posture?.goose_latest_gateway_execution_id || "none")} | report=${escapeHtml(overlay.runtime_posture?.goose_latest_gateway_report_id || "none")} | resolution=${escapeHtml(overlay.runtime_posture?.goose_latest_gateway_resolution_id || "none")} | bundle=${escapeHtml(overlay.runtime_posture?.goose_latest_gateway_extension_bundle_id || "none")} | policy=${escapeHtml(overlay.runtime_posture?.goose_latest_gateway_policy_set_id || "none")} | family=${escapeHtml(overlay.runtime_posture?.goose_latest_gateway_bundle_family || "none")} | latest-families=${escapeHtml((overlay.runtime_posture?.goose_latest_gateway_flow_families || []).join(", ") || "none")} | family-counts=${escapeHtml(JSON.stringify(overlay.runtime_posture?.goose_gateway_flow_family_counts || {}))} | trace=${escapeHtml(overlay.runtime_posture?.goose_latest_gateway_trace_id || "none")} | report-link=${escapeHtml(overlay.runtime_posture?.goose_latest_gateway_linked_report_id || "none")} | adv=${escapeHtml(overlay.runtime_posture?.goose_latest_gateway_adversary_report_id || "none")}</small></div>
    <div class="inspect-row"><small><strong>Goose scheduled:</strong> history=${escapeHtml(String(overlay.runtime_posture?.goose_scheduled_history_count || 0))} | latest-artifact=${escapeHtml(overlay.runtime_posture?.goose_latest_scheduled_artifact_id || "none")} | latest-report=${escapeHtml(overlay.runtime_posture?.goose_latest_scheduled_report_id || "none")} | source-exec=${escapeHtml(overlay.runtime_posture?.goose_latest_scheduled_execution_id || "none")} | trace=${escapeHtml(overlay.runtime_posture?.goose_latest_scheduled_linked_trace_id || "none")} | report-link=${escapeHtml(overlay.runtime_posture?.goose_latest_scheduled_linked_report_id || "none")} | gateway=${escapeHtml(overlay.runtime_posture?.goose_latest_scheduled_gateway_resolution_id || "none")}</small></div>
    <div class="inspect-row"><small><strong>Goose extensions:</strong> total=${escapeHtml(String(overlay.runtime_posture?.goose_extension_count || 0))} | enabled=${escapeHtml(String(overlay.runtime_posture?.goose_enabled_extension_count || 0))} | approval-required=${escapeHtml(String(overlay.runtime_posture?.goose_extension_approval_required_count || 0))} | high-risk=${escapeHtml(String(overlay.runtime_posture?.goose_extension_high_risk_count || 0))} | policy-sets=${escapeHtml(String(overlay.runtime_posture?.goose_extension_policy_set_count || overlay.runtime_posture?.goose_extension_policy_catalog_count || 0))} | policy-history=${escapeHtml(String(overlay.runtime_posture?.goose_policy_history_count || 0))} | rollout-families=${escapeHtml(String(overlay.runtime_posture?.goose_policy_rollout_family_count || 0))} | certifications=${escapeHtml(String(overlay.runtime_posture?.goose_certification_artifact_count || 0))} | families=${escapeHtml(String(overlay.runtime_posture?.goose_extension_bundle_family_count || 0))} | latest-bundle=${escapeHtml(overlay.runtime_posture?.goose_latest_extension_bundle_id || "none")} | latest-policy=${escapeHtml(overlay.runtime_posture?.goose_latest_extension_policy_set_id || "none")}@${escapeHtml(overlay.runtime_posture?.goose_latest_extension_policy_set_version || "none")} | policy-status=${escapeHtml(overlay.runtime_posture?.goose_latest_policy_status || "none")} | family=${escapeHtml(overlay.runtime_posture?.goose_latest_extension_bundle_family || "none")} | latest-artifact=${escapeHtml(overlay.runtime_posture?.goose_latest_extension_bundle_artifact_id || "none")} | latest-report=${escapeHtml(overlay.runtime_posture?.goose_latest_extension_bundle_report_id || "none")} | lifecycle-artifact=${escapeHtml(overlay.runtime_posture?.goose_latest_policy_history_artifact_id || "none")} | certification=${escapeHtml(overlay.runtime_posture?.goose_latest_certification_status || "none")} | certification-artifact=${escapeHtml(overlay.runtime_posture?.goose_latest_certification_artifact_id || "none")} | acp-providers=${escapeHtml(String(overlay.runtime_posture?.goose_acp_provider_count || 0))} | acp-enabled=${escapeHtml(String(overlay.runtime_posture?.goose_acp_enabled ?? false))}</small></div>
    <div class="inspect-row"><small><strong>Goose ACP:</strong> ready=${escapeHtml(String(overlay.runtime_posture?.goose_acp_ready_count || 0))} | blocked=${escapeHtml(String(overlay.runtime_posture?.goose_acp_blocked_probe_count || 0))} | provider-gated=${escapeHtml(String(overlay.runtime_posture?.goose_acp_provider_gated_count || 0))} | misconfigured=${escapeHtml(String(overlay.runtime_posture?.goose_acp_misconfigured_count || 0))} | version-mismatch=${escapeHtml(String(overlay.runtime_posture?.goose_acp_version_mismatch_count || 0))} | version-ok=${escapeHtml(String(overlay.runtime_posture?.goose_acp_version_compatible_count || 0))} | feature-ok=${escapeHtml(String(overlay.runtime_posture?.goose_acp_feature_compatible_count || 0))} | feature-missing=${escapeHtml(String(overlay.runtime_posture?.goose_acp_feature_incompatible_count || 0))} | probe-modes=${escapeHtml(JSON.stringify(overlay.runtime_posture?.goose_acp_probe_mode_counts || {}))} | probe-statuses=${escapeHtml(JSON.stringify(overlay.runtime_posture?.goose_acp_probe_status_counts || {}))} | readiness=${escapeHtml(JSON.stringify(overlay.runtime_posture?.goose_acp_probe_readiness_state_counts || {}))} | live-capable=${escapeHtml(String(overlay.runtime_posture?.goose_acp_live_probe_capable_count || 0))} | live-active=${escapeHtml(String(overlay.runtime_posture?.goose_acp_live_probe_active_count || 0))} | simulated=${escapeHtml(String(overlay.runtime_posture?.goose_acp_simulated_probe_count || 0))} | fixtures=${escapeHtml(String(overlay.runtime_posture?.goose_acp_compatibility_fixture_count || 0))} | probes=${escapeHtml(String(overlay.runtime_posture?.goose_acp_live_probe_example_count || 0))} | statuses=${escapeHtml(JSON.stringify(overlay.runtime_posture?.goose_acp_status_counts || {}))} | blockers=${escapeHtml(JSON.stringify(overlay.runtime_posture?.goose_acp_live_probe_blocker_counts || {}))} | remediation=${escapeHtml(JSON.stringify(overlay.runtime_posture?.goose_acp_remediation_action_counts || {}))} | gaps=${escapeHtml(JSON.stringify(overlay.runtime_posture?.goose_acp_config_gap_counts || {}))}</small></div>
    <div class="inspect-row"><small><strong>Goose workers:</strong> runs=${escapeHtml(String(overlay.runtime_posture?.goose_subagent_run_count || 0))} | latest=${escapeHtml(overlay.runtime_posture?.goose_latest_subagent_run_id || "none")} | gateway=${escapeHtml(overlay.runtime_posture?.goose_latest_subagent_gateway_resolution_id || "none")} | privilege-review=${escapeHtml(overlay.runtime_posture?.goose_latest_subagent_privilege_review_id || "none")} | permission=${escapeHtml(overlay.runtime_posture?.goose_permission_mode || "none")} | sandbox=${escapeHtml(overlay.runtime_posture?.goose_sandbox_profile || "none")}</small></div>
    <div class="inspect-row"><small><strong>Goose guardrails:</strong> injected=${escapeHtml(String(overlay.runtime_posture?.goose_guardrail_count || 0))} | adversary=${escapeHtml(overlay.runtime_posture?.goose_latest_adversary_review_id || "none")} | decision=${escapeHtml(overlay.runtime_posture?.goose_latest_adversary_decision || "none")} | report=${escapeHtml(overlay.runtime_posture?.goose_latest_adversary_report_id || "none")} | audit-export=${escapeHtml(overlay.runtime_posture?.goose_latest_adversary_audit_export_id || "none")} | trigger=${escapeHtml(overlay.runtime_posture?.goose_latest_adversary_trigger_source || "none")}</small></div>
    <div class="inspect-row"><small><strong>Goose adversary families:</strong> ${escapeHtml(JSON.stringify(overlay.runtime_posture?.goose_adversary_family_counts || {}))}</small></div>
    <div class="inspect-row"><small><strong>Goose compare refs:</strong> gateway=${escapeHtml(overlay.runtime_posture?.goose_gateway_compare_ref || "none")} | policy=${escapeHtml(overlay.runtime_posture?.goose_policy_history_compare_ref || "none")} | certification=${escapeHtml(overlay.runtime_posture?.goose_certification_compare_ref || "none")} | adversary=${escapeHtml(overlay.runtime_posture?.goose_adversary_compare_ref || "none")} | acp=${escapeHtml(overlay.runtime_posture?.goose_acp_compare_ref || "none")}</small></div>
    <div class="inspect-row"><small><strong>Goose compare catalog:</strong> gateway=${escapeHtml(String(gooseCompareCatalog.gateway_execution_count || 0))} | policy=${escapeHtml(String(gooseCompareCatalog.policy_version_count || 0))} | certification=${escapeHtml(String(gooseCompareCatalog.certification_count || 0))} | adversary=${escapeHtml(String(gooseCompareCatalog.adversary_review_count || 0))} | acp=${escapeHtml(String(gooseCompareCatalog.acp_provider_count || 0))}</small></div>
    <div class="inspect-row"><small><strong>Goose diff groups:</strong> ${(gooseCompareCatalog.group_names || []).map(escapeHtml).join(" | ") || "none"}</small></div>
    <div class="inspect-row"><small><strong>AITune supported lane:</strong> ${escapeHtml(overlay.runtime_posture?.aitune_supported_lane_status || "unreported")} | health=${escapeHtml(overlay.runtime_posture?.aitune_provider_health || "unknown")} | latest=${escapeHtml(overlay.runtime_posture?.aitune_latest_validation_status || "none")}</small></div>
    <div class="inspect-row"><small><strong>AITune artifacts:</strong> validation=${escapeHtml(overlay.runtime_posture?.aitune_latest_validation_artifact_id || "none")} | plan=${escapeHtml(overlay.runtime_posture?.aitune_latest_execution_plan_id || "none")} | runner=${escapeHtml(overlay.runtime_posture?.aitune_latest_runner_artifact_id || "none")}</small></div>
    <div class="inspect-row"><small><strong>AITune outputs:</strong> benchmark=${escapeHtml(overlay.runtime_posture?.aitune_latest_benchmark_id || "none")} | tuned=${escapeHtml(overlay.runtime_posture?.aitune_latest_tuned_artifact_id || "none")} | markdown=${escapeHtml(overlay.runtime_posture?.aitune_latest_execution_plan_markdown_path || "none")}</small></div>
    <div class="inspect-row"><small><strong>AITune skip reason:</strong> ${escapeHtml(overlay.runtime_posture?.aitune_skip_reason || "none")}</small></div>
    <div class="inspect-row"><small><strong>TriAttention scorecard:</strong> ${escapeHtml(overlay.runtime_posture?.triattention_latest_scorecard_id || "none")} | report=${escapeHtml(overlay.runtime_posture?.triattention_latest_report_id || "none")} | baselines=${escapeHtml(String(overlay.runtime_posture?.triattention_baseline_count || 0))} | anchors=${escapeHtml(String(overlay.runtime_posture?.triattention_runtime_anchor_count || 0))}</small></div>
    <div class="inspect-row"><small><strong>TriAttention runtime anchors:</strong> available=${escapeHtml(String(overlay.runtime_posture?.triattention_runtime_anchor_live_count || 0))} | latency-anchored=${escapeHtml(String(overlay.runtime_posture?.triattention_runtime_anchor_latency_anchored_count || 0))} | modes=${escapeHtml(JSON.stringify(overlay.runtime_posture?.triattention_runtime_anchor_measurement_modes || {}))}</small></div>
    <div class="inspect-row"><small><strong>OBLITERATUS safe lane:</strong> quarantine=${escapeHtml(String(overlay.runtime_posture?.obliteratus_quarantine_required ?? false))} | latest-review=${escapeHtml(overlay.runtime_posture?.obliteratus_latest_review_id || "none")} | research-only</small></div>
  `;
}

function renderDepthInspection(now = performance.now()) {
  const canvas = dom.depthCanvas;
  const ctx = canvas?.getContext?.("2d");
  if (!ctx || !canvas) {
    return;
  }
  const rect = canvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  const width = Math.max(1, Math.round(rect.width * dpr));
  const height = Math.max(1, Math.round(rect.height * dpr));
  if (canvas.width !== width || canvas.height !== height) {
    canvas.width = width;
    canvas.height = height;
  }
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, rect.width, rect.height);

  if (!dom.toggleDepthView.checked) {
    dom.depthStatus.innerHTML = "<small>Depth subrenderer disabled.</small>";
    return;
  }
  const node = state.scene?.nodes?.find((candidate) => candidate.node_id === state.selectedNodeId);
  if (!node) {
    dom.depthStatus.innerHTML = "<small>Select the core or a capsule to inspect depth.</small>";
    return;
  }
  const tier = effectiveRenderTier();
  const points = (node.internal_nodes || []).slice(0, tier === "safe" ? 18 : tier === "balanced" ? 30 : 48);
  const rotation = now / 1800;
  const centerX = rect.width / 2;
  const centerY = rect.height / 2;
  const projected = [];
  for (const [index, point] of points.entries()) {
    const syntheticZ = Number(point.layer_index || 0) * 12 + Math.sin(index * 0.7 + rotation) * 18;
    const rotatedX = point.x * Math.cos(rotation) - syntheticZ * Math.sin(rotation) * 0.42;
    const projectedY = point.y + syntheticZ * 0.18;
    const radius = node.node_type === "core" ? 4.2 : 3.2;
    const alpha = 0.25 + Math.max(0, (syntheticZ + 24) / 80) * 0.5;
    projected.push({
      x: centerX + rotatedX * 1.2,
      y: centerY + projectedY * 1.1,
      z: syntheticZ,
      alpha,
    });
    ctx.fillStyle = node.node_type === "core" ? `rgba(111, 231, 255, ${alpha})` : `rgba(125, 160, 255, ${alpha})`;
    ctx.beginPath();
    ctx.arc(centerX + rotatedX * 1.2, centerY + projectedY * 1.1, radius, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.strokeStyle = "rgba(255,255,255,0.08)";
  ctx.strokeRect(10, 10, rect.width - 20, rect.height - 20);

  const meshSegments = buildMeshSegments(node).slice(0, tier === "safe" ? 20 : 36);
  for (const segment of meshSegments) {
    const left = projected.find((candidate, index) => points[index]?.id === segment.source.id);
    const right = projected.find((candidate, index) => points[index]?.id === segment.target.id);
    if (!left || !right) {
      continue;
    }
    const alpha = Math.max(0.06, Math.min(left.alpha, right.alpha) * 0.44);
    ctx.strokeStyle = node.node_type === "core" ? `rgba(111, 231, 255, ${alpha})` : `rgba(125, 160, 255, ${alpha})`;
    ctx.lineWidth = tier === "safe" ? 0.8 : 1.1;
    ctx.beginPath();
    ctx.moveTo(left.x, left.y);
    ctx.lineTo(right.x, right.y);
    ctx.stroke();
  }

  for (const port of portPositions(node)) {
    ctx.strokeStyle = "rgba(255,255,255,0.18)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(centerX + port.x * 0.82, centerY + port.y * 0.82, node.node_type === "core" ? 4.8 : 3.8, 0, Math.PI * 2);
    ctx.stroke();
  }

  ctx.fillStyle = "rgba(255,255,255,0.62)";
  ctx.font = "12px Cascadia Mono, Consolas, monospace";
  ctx.fillText(node.topology_id || "nexus-core", 18, rect.height - 18);
  dom.depthStatus.innerHTML = `<small>${escapeHtml(node.label)} | ${escapeHtml(node.topology_id || "nexus-core")} | ${escapeHtml(String(points.length))} depth nodes | ${escapeHtml(String(meshSegments.length))} mesh links</small>`;
}

function renderDiffCard(payload, title) {
  if (!payload) {
    dom.diffCard.innerHTML = "No diff loaded yet.";
    state.activeDiff = null;
    state.activeDiffTitle = title || "Diff";
    renderGooseCompareControls({ domain: null, groups: [] });
    return;
  }
  const resetGooseCompare = payload !== state.activeDiff;
  state.activeDiff = payload;
  state.activeDiffTitle = title;
  const leftId = payload.left?.bundle_id || payload.left?.policy_set_id || payload.left?.provider_id || payload.left?.review_id || payload.left?.artifact_id || payload.left?.report_id || payload.left?.cohort_id || payload.left?.execution_id || "left";
  const rightId = payload.right?.bundle_id || payload.right?.policy_set_id || payload.right?.provider_id || payload.right?.review_id || payload.right?.artifact_id || payload.right?.report_id || payload.right?.cohort_id || payload.right?.execution_id || "right";
  const sceneDelta = payload.scene_delta || {};
  const diffSummary = summarizeDiffEntries(payload.diff || {});
  const subjectRow = (sceneDelta.hot_subjects || [])
    .slice(0, 6)
    .map((item) => `<span class="diff-chip">${escapeHtml(item.subject)} ${item.delta > 0 ? "+" : ""}${escapeHtml(item.delta)}</span>`)
    .join("");
  const linkRow = (sceneDelta.hot_links || [])
    .slice(0, 4)
    .map((item) => `<span class="diff-chip">${escapeHtml(item.link_id)} ${item.delta > 0 ? "+" : ""}${escapeHtml(item.delta)}</span>`)
    .join("");
  const summaryRow = diffSummary
    .map((item) => `<span class="diff-chip">${escapeHtml(item)}</span>`)
    .join("");
  const exportId = payload.export?.report_id || payload.export?.export_id || "none";
  const exportPayloadPath = payload.export?.payload_path || "none";
  const exportMarkdownPath = payload.export?.markdown_path || "none";
  const sceneRefSummary = summarizeSceneRefs(sceneDelta);
  const diffCount = Object.keys(payload.diff || {}).length;
  const diffDomain = detectDiffDomain(payload);
  const groupedDiffs = buildDiffGroups(payload);
  syncGooseCompareState({ domain: diffDomain, groups: groupedDiffs, reset: resetGooseCompare });
  renderGooseCompareControls({ domain: diffDomain, groups: groupedDiffs });
  const visibleGroups = gooseCompareGroupsForRender(groupedDiffs);
  const groupedSections = visibleGroups
    .map((group, index) => renderDiffGroup(group, gooseCompareGroupOpen(group.id, index)))
    .join("");
  dom.diffCard.innerHTML = `
    <div class="inspect-row">
      <strong>${escapeHtml(title)}</strong>
      <small class="mono">read-only</small>
    </div>
    <div class="diff-columns">
      <div class="inspect-row">
        <strong>${escapeHtml(leftId)}</strong>
        <small>${escapeHtml(payload.left?.subject || payload.left?.teacher_id || payload.left?.registry_layer || "left")}</small>
      </div>
      <div class="inspect-row">
        <strong>${escapeHtml(rightId)}</strong>
        <small>${escapeHtml(payload.right?.subject || payload.right?.teacher_id || payload.right?.registry_layer || "right")}</small>
      </div>
    </div>
    <div class="inspect-row"><small><strong>Summary:</strong> ${escapeHtml(payload.human_summary || payload.export?.human_summary || payload.detail || "No summary available.")}</small></div>
    <div class="inspect-row"><small><strong>Export:</strong> ${escapeHtml(exportId)} | payload=${escapeHtml(exportPayloadPath)} | markdown=${escapeHtml(exportMarkdownPath)}</small></div>
    <div class="inspect-row"><small><strong>Diff shape:</strong> domain=${escapeHtml(diffDomain)} | ${escapeHtml(String(diffCount))} fields | scene-refs=${escapeHtml(sceneRefSummary || "none")}</small></div>
    <div class="diff-chip-row">${summaryRow || '<span class="diff-chip">No structured diff summary</span>'}</div>
    <div class="diff-chip-row">${subjectRow || '<span class="diff-chip">No subject delta</span>'}</div>
    <div class="diff-chip-row">${linkRow || '<span class="diff-chip">No link delta</span>'}</div>
    <div class="inspect-row"><small><strong>Scene refs:</strong> ${escapeHtml(sceneRefSummary || JSON.stringify(sceneDelta.refs || {}))}</small></div>
    <div class="inspect-row"><small><strong>Grouped diff sections:</strong> ${escapeHtml(visibleGroups.map((group) => group.label).join(" | ") || "none")} | all=${escapeHtml(groupedDiffs.map((group) => group.label).join(" | ") || "none")}</small></div>
    ${groupedSections || ""}
    <details>
      <summary class="mono">Raw diff</summary>
      <pre class="mono">${escapeHtml(JSON.stringify(payload.diff || payload, null, 2))}</pre>
    </details>
  `;
  updateActiveClasses();
  renderOperatorCard();
}

function renderReplayStatus() {
  const frame = state.replay.frames?.[state.replay.index];
  if (!frame) {
    dom.replayStatus.innerHTML = "<small>No replay loaded yet.</small>";
    return;
  }
  const anchor = state.replay.frames?.[state.replay.anchorIndex];
  dom.replayStatus.innerHTML = `
    <small><strong>${escapeHtml(frame.frame_id)}</strong></small>
    <small>${escapeHtml(frame.selected_expert || "idle")} | ${escapeHtml(frame.lineage || "live-derived")} | ${state.replay.enabled ? "replay-active" : "live-overlay"} | anchor=${escapeHtml(anchor?.frame_id || "none")}</small>
  `;
}

function renderReplayTimeline() {
  const frames = state.replay.frames || [];
  if (!frames.length) {
    dom.timelineCard.innerHTML = "<small>No replay timeline yet.</small>";
    return;
  }
  dom.timelineCard.innerHTML = `
    <div class="inspect-row">
      <strong>Replay Timeline</strong>
      <small>${escapeHtml(String(frames.length))} frames</small>
    </div>
    ${frames.map((frame, index) => `
      <button
        class="timeline-item ${index === state.replay.index ? "active" : ""} ${index === state.replay.anchorIndex ? "anchor" : ""}"
        data-replay-index="${index}"
        data-frame-action="focus"
      >
        <span class="timeline-main">${escapeHtml(frame.selected_expert || "idle")}</span>
        <span class="timeline-meta">${escapeHtml(frame.lineage || "live-derived")} | ${escapeHtml(frame.created_at || frame.frame_id || "frame")}</span>
        <span class="timeline-badge" data-replay-index="${index}" data-frame-action="anchor">${index === state.replay.anchorIndex ? "Anchor" : "Set Anchor"}</span>
      </button>
    `).join("")}
  `;
}

async function loadReplay() {
  const limit = Number(dom.filterTraceWindow.value || 12);
  const payload = await fetchJSON(`/ops/brain/visualizer/replay?session_id=${encodeURIComponent(dom.sessionInput.value || sessionId())}&limit=${limit}`);
  state.replay.frames = payload.frames || [];
  state.replay.index = 0;
  state.replay.anchorIndex = 0;
  state.replay.enabled = false;
  dom.replayRange.max = String(Math.max(0, state.replay.frames.length - 1));
  dom.replayRange.value = "0";
  dom.replayAnchorRange.max = String(Math.max(0, state.replay.frames.length - 1));
  dom.replayAnchorRange.value = "0";
  renderReplayStatus();
  renderReplayTimeline();
  renderOperatorCard();
  updateActiveClasses();
}

function drawAmbientFrame(now) {
  if (state.performance.lastNow) {
    recordFrameTime(now - state.performance.lastNow);
  }
  state.performance.lastNow = now;
  const ctx = dom.fxCanvas.getContext("2d");
  if (!ctx || !state.scene) {
    state.animationHandle = requestAnimationFrame(drawAmbientFrame);
    return;
  }
  const rect = dom.fxCanvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  const width = Math.max(1, Math.round(rect.width * dpr));
  const height = Math.max(1, Math.round(rect.height * dpr));
  if (dom.fxCanvas.width !== width || dom.fxCanvas.height !== height) {
    dom.fxCanvas.width = width;
    dom.fxCanvas.height = height;
  }
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, rect.width, rect.height);

  const mode = currentMode();
  const tier = effectiveRenderTier();
  const overlay = effectiveOverlay();
  const coreNode = state.scene.nodes.find((node) => node.node_type === "core");
  const core = coreNode ? sceneToScreen(coreNode.x, coreNode.y) : { x: rect.width / 2, y: rect.height / 2 };
  const time = now / 1000;
  const radius = Math.min(rect.width, rect.height) * (mode?.mode_id === "cinematic" ? 0.52 : 0.4) * (tier === "safe" ? 0.88 : 1);
  const lowPower = state.performance.lowPower || tier === "safe";

  if (!lowPower) {
    const field = ctx.createRadialGradient(core.x, core.y, 0, core.x, core.y, radius);
    field.addColorStop(0, "rgba(111, 231, 255, 0.18)");
    field.addColorStop(0.34, mode?.mode_id === "cinematic" ? "rgba(154, 125, 255, 0.18)" : "rgba(125, 160, 255, 0.12)");
    field.addColorStop(1, "rgba(0, 0, 0, 0)");
    ctx.fillStyle = field;
    ctx.fillRect(0, 0, rect.width, rect.height);
  }

  const activeSubjects = new Set(overlay.active_subjects || []);
  for (const node of state.scene.nodes.filter((candidate) => candidate.node_type !== "subnode")) {
    const point = sceneToScreen(node.x, node.y);
    const intensity = node.subject ? (overlay.link_activity?.core_to_capsule?.[node.subject]?.intensity || 0) : 1;
    const glowRadius = node.node_type === "core" ? (tier === "safe" ? 88 : 120) : (tier === "safe" ? 44 : 64);
    const active = node.subject && activeSubjects.has(node.subject);
    if (lowPower && !active && intensity < 0.18 && node.node_type !== "core") {
      continue;
    }
    const glow = ctx.createRadialGradient(point.x, point.y, 0, point.x, point.y, glowRadius);
    glow.addColorStop(0, active || intensity > 0.2 ? "rgba(111, 231, 255, 0.34)" : "rgba(125, 160, 255, 0.12)");
    glow.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = glow;
    ctx.beginPath();
    ctx.arc(point.x, point.y, glowRadius, 0, Math.PI * 2);
    ctx.fill();
  }

  if (dom.togglePhysiology.checked) {
    const physiology = overlay.safe_mode_physiology || {};
    const physiologyActivity = overlay.physiology_activity || {};
    if ((physiologyActivity.thermal?.intensity || 0) > 0) {
      ctx.fillStyle = `rgba(255, 159, 67, ${0.03 + (physiologyActivity.thermal?.intensity || 0) * 0.06})`;
      ctx.fillRect(0, 0, rect.width, rect.height);
    }
    if ((physiologyActivity.retry?.intensity || 0) > 0) {
      ctx.strokeStyle = "rgba(255, 111, 145, 0.2)";
      ctx.lineWidth = tier === "safe" ? 1.5 : 2;
      ctx.beginPath();
      ctx.arc(core.x, core.y, 160 + Math.sin(time * 3) * 18, 0, Math.PI * 2);
      ctx.stroke();
    }
    if ((physiologyActivity.vram?.intensity || 0) > 0 || (physiologyActivity.ram?.intensity || 0) > 0) {
      ctx.strokeStyle = "rgba(255, 209, 102, 0.18)";
      ctx.lineWidth = 1;
      ctx.setLineDash([10, 8]);
      ctx.beginPath();
      ctx.arc(core.x, core.y, 210 + Math.sin(time * 2.2) * 10, 0, Math.PI * 2);
      ctx.stroke();
      ctx.setLineDash([]);
    }
    if (physiology.safe_mode) {
      ctx.strokeStyle = "rgba(139, 211, 221, 0.14)";
      ctx.lineWidth = 1.5;
      ctx.strokeRect(20, 20, rect.width - 40, rect.height - 40);
    }
  }

  document.body.classList.toggle("reduced-motion", state.performance.reducedMotion);
  renderDepthInspection(now);

  state.animationHandle = requestAnimationFrame(drawAmbientFrame);
}

async function loadOverlay() {
  const overlay = await fetchJSON(`/ops/brain/visualizer/state?session_id=${encodeURIComponent(dom.sessionInput.value || sessionId())}`);
  state.overlay = overlay;
  dom.overlayStatus.textContent = `Overlay: ${overlay.overlay_state?.active_registry_layer || "pending"} / ${overlay.overlay_state?.route_activity?.selected_expert || "idle"} / ${overlay.overlay_state?.performance_profile?.recommended_tier || "balanced"}`;
  renderFilterControls();
  renderLivePosture();
  renderEvidenceCards();
  renderReplayStatus();
  renderOperatorCard();
  updateActiveClasses();
}

async function bootstrap() {
  dom.sessionInput.value = sessionId();
  state.scene = await fetchJSON("./data/scene.json");
  state.currentMode = state.scene.default_mode_id;
  dom.renderTierSelect.value = "auto";
  dom.toggleLowPower.checked = state.performance.lowPower;
  renderModePills();
  renderLegend();
  renderGrid();
  renderLinks();
  renderLoops();
  renderNodes();
  applyViewBox();
  dom.sceneStatus.textContent = `${state.scene.manifest.title} | ${state.scene.nodes.filter((node) => node.node_type === "capsule").length} expert capsules`;
  selectNode(state.scene.nodes.find((node) => node.node_type === "core")?.node_id);
  await loadOverlay();
  await loadReplay();
  cancelAnimationFrame(state.animationHandle);
  drawAmbientFrame(performance.now());
  setInterval(loadOverlay, 8000);
}

dom.refreshButton.addEventListener("click", () => loadOverlay().catch((error) => {
  dom.overlayStatus.textContent = `Overlay error: ${error.message}`;
}));

dom.resetViewButton.addEventListener("click", () => {
  animateViewBox({ ...DEFAULT_VIEWBOX });
  selectNode(state.scene?.nodes?.find((node) => node.node_type === "core")?.node_id || null);
});

[dom.toggleDream, dom.toggleCritique, dom.toggleConsequence].forEach((toggle) => {
  toggle.addEventListener("change", renderLoops);
});

[
  dom.filterRegistryLayer,
  dom.filterSubject,
  dom.filterTeacherPair,
  dom.filterPromotionKind,
  dom.filterTakeoverStatus,
  dom.filterBenchmarkFamily,
  dom.filterThresholdSet,
  dom.filterEvidenceBundle,
  dom.filterDisagreement,
  dom.filterLineage,
  dom.filterTraceWindow,
  dom.filterSafePosture,
].forEach((input) => {
  input?.addEventListener("change", () => {
    updateActiveClasses();
    if (input === dom.filterTraceWindow) {
      loadReplay().catch((error) => {
        dom.replayStatus.innerHTML = `<small>${escapeHtml(error.message)}</small>`;
      });
    }
  });
});

dom.togglePhysiology.addEventListener("change", () => {
  renderLivePosture();
  updateActiveClasses();
});

dom.renderTierSelect.addEventListener("change", () => {
  state.renderTier = dom.renderTierSelect.value || "auto";
  renderLivePosture();
  renderOperatorCard();
});

dom.reloadReplayButton.addEventListener("click", () => loadReplay().catch((error) => {
  dom.replayStatus.innerHTML = `<small>${escapeHtml(error.message)}</small>`;
}));

dom.replayRange.addEventListener("input", () => {
  state.replay.index = Number(dom.replayRange.value || 0);
  state.replay.enabled = true;
  renderReplayStatus();
  renderReplayTimeline();
  updateActiveClasses();
  renderLivePosture();
  renderEvidenceCards();
  renderOperatorCard();
});

dom.replayAnchorRange.addEventListener("input", () => {
  state.replay.anchorIndex = Number(dom.replayAnchorRange.value || 0);
  renderReplayStatus();
  renderReplayTimeline();
  renderOperatorCard();
});

dom.toggleReplayButton.addEventListener("click", () => {
  state.replay.playing = !state.replay.playing;
  state.replay.enabled = state.replay.playing;
  dom.toggleReplayButton.textContent = state.replay.playing ? "Pause Replay" : "Play Replay";
  if (!state.replay.playing) {
    clearInterval(state.replayTimer);
    state.replay.enabled = false;
    renderReplayStatus();
    renderReplayTimeline();
    updateActiveClasses();
    renderLivePosture();
    renderEvidenceCards();
    renderOperatorCard();
    return;
  }
  clearInterval(state.replayTimer);
  state.replayTimer = setInterval(() => {
    if (!state.replay.frames.length) {
      return;
    }
    state.replay.index = (state.replay.index + 1) % state.replay.frames.length;
    dom.replayRange.value = String(state.replay.index);
    renderReplayStatus();
    renderReplayTimeline();
    updateActiveClasses();
    renderLivePosture();
    renderEvidenceCards();
    renderOperatorCard();
  }, 1400);
});

async function loadDiff(url, title) {
  const payload = await fetchJSON(url);
  renderDiffCard(payload, title);
}

function buildReplayDiffPayload(leftFrame, rightFrame, title) {
  if (!leftFrame || !rightFrame) {
    return { detail: "Replay comparison requires two valid frames." };
  }
  const leftOverlay = {
    active_subjects: leftFrame.overlay?.active_subjects || [],
    link_activity: leftFrame.overlay?.link_activity || {},
  };
  const rightOverlay = {
    active_subjects: rightFrame.overlay?.active_subjects || [],
    link_activity: rightFrame.overlay?.link_activity || {},
  };
  return {
    left: { frame_id: leftFrame.frame_id, subject: leftFrame.selected_expert, lineage: leftFrame.lineage },
    right: { frame_id: rightFrame.frame_id, subject: rightFrame.selected_expert, lineage: rightFrame.lineage },
    scene_delta: {
      hot_subjects: computeReplaySubjectDelta(leftOverlay, rightOverlay),
      hot_links: computeReplayLinkDelta(leftOverlay, rightOverlay),
    },
    diff: {
      left_frame_id: leftFrame.frame_id,
      right_frame_id: rightFrame.frame_id,
      left_lineage: leftFrame.lineage,
      right_lineage: rightFrame.lineage,
      left_refs: leftFrame.refs || {},
      right_refs: rightFrame.refs || {},
    },
    title,
  };
}

function computeReplaySubjectDelta(leftOverlay, rightOverlay) {
  const leftSubjects = leftOverlay.link_activity?.core_to_capsule || {};
  const rightSubjects = rightOverlay.link_activity?.core_to_capsule || {};
  return [...new Set([...Object.keys(leftSubjects), ...Object.keys(rightSubjects)])]
    .map((subject) => ({
      subject,
      delta: Number(((rightSubjects[subject]?.intensity || 0) - (leftSubjects[subject]?.intensity || 0)).toFixed(3)),
    }))
    .filter((item) => item.delta !== 0)
    .sort((left, right) => Math.abs(right.delta) - Math.abs(left.delta))
    .slice(0, 12);
}

function computeReplayLinkDelta(leftOverlay, rightOverlay) {
  const leftEdges = leftOverlay.link_activity?.edges || {};
  const rightEdges = rightOverlay.link_activity?.edges || {};
  return [...new Set([...Object.keys(leftEdges), ...Object.keys(rightEdges)])]
    .map((linkId) => ({
      link_id: linkId,
      delta: Number(((rightEdges[linkId]?.intensity || 0) - (leftEdges[linkId]?.intensity || 0)).toFixed(3)),
    }))
    .filter((item) => item.delta !== 0)
    .sort((left, right) => Math.abs(right.delta) - Math.abs(left.delta))
    .slice(0, 16);
}

dom.compareBundleButton.addEventListener("click", () => {
  if (!dom.compareBundleLeft.value || !dom.compareBundleRight.value) {
    renderDiffCard({ detail: "Choose two evidence bundles first." }, "Bundle Diff");
    return;
  }
  loadDiff(
    `/ops/brain/teachers/evidence/diff?left_bundle_id=${encodeURIComponent(dom.compareBundleLeft.value)}&right_bundle_id=${encodeURIComponent(dom.compareBundleRight.value)}`,
    "Bundle Diff",
  ).catch((error) => renderDiffCard({ detail: error.message }, "Bundle Diff"));
});

dom.compareDisagreementButton.addEventListener("click", () => {
  if (!dom.compareDisagreementLeft.value || !dom.compareDisagreementRight.value) {
    renderDiffCard({ detail: "Choose two disagreement artifacts first." }, "Disagreement Diff");
    return;
  }
  loadDiff(
    `/ops/brain/visualizer/disagreements/compare?left_artifact_id=${encodeURIComponent(dom.compareDisagreementLeft.value)}&right_artifact_id=${encodeURIComponent(dom.compareDisagreementRight.value)}`,
    "Disagreement Diff",
  ).catch((error) => renderDiffCard({ detail: error.message }, "Disagreement Diff"));
});

dom.compareReplacementButton.addEventListener("click", () => {
  if (!dom.compareReplacementLeft.value || !dom.compareReplacementRight.value) {
    renderDiffCard({ detail: "Choose two readiness reports first." }, "Replacement Readiness Diff");
    return;
  }
  loadDiff(
    `/ops/brain/visualizer/replacement-readiness/compare?left_report_id=${encodeURIComponent(dom.compareReplacementLeft.value)}&right_report_id=${encodeURIComponent(dom.compareReplacementRight.value)}`,
    "Replacement Readiness Diff",
  ).catch((error) => renderDiffCard({ detail: error.message }, "Replacement Readiness Diff"));
});

dom.compareRouteButton.addEventListener("click", () => {
  const rightWindow = Number(dom.filterTraceWindow.value || 24);
  const leftWindow = Math.max(6, Math.floor(rightWindow / 2));
  loadDiff(
    `/ops/brain/visualizer/route-activity/compare?session_id=${encodeURIComponent(dom.sessionInput.value || sessionId())}&left_window=${leftWindow}&right_window=${rightWindow}`,
    "Route Window Diff",
  ).catch((error) => renderDiffCard({ detail: error.message }, "Route Window Diff"));
});

dom.compareGooseGatewayButton.addEventListener("click", () => {
  if (!dom.compareGooseGatewayLeft.value || !dom.compareGooseGatewayRight.value) {
    renderDiffCard({ detail: "Choose two gateway executions first." }, "Goose Gateway Diff");
    return;
  }
  loadDiff(
    `/ops/brain/gateway/history/compare?left_execution_id=${encodeURIComponent(dom.compareGooseGatewayLeft.value)}&right_execution_id=${encodeURIComponent(dom.compareGooseGatewayRight.value)}`,
    "Goose Gateway Diff",
  ).catch((error) => renderDiffCard({ detail: error.message }, "Goose Gateway Diff"));
});

dom.compareGoosePolicyButton.addEventListener("click", () => {
  const left = parseGoosePolicySelection(dom.compareGoosePolicyLeft.value);
  const right = parseGoosePolicySelection(dom.compareGoosePolicyRight.value);
  if (!left.policySetId || !right.policySetId) {
    renderDiffCard({ detail: "Choose two policy versions first." }, "Goose Policy Diff");
    return;
  }
  loadDiff(
    `/ops/brain/extensions/policy-history/compare?left_policy_set_id=${encodeURIComponent(left.policySetId)}&right_policy_set_id=${encodeURIComponent(right.policySetId)}&left_version=${encodeURIComponent(left.version || "")}&right_version=${encodeURIComponent(right.version || "")}`,
    "Goose Policy Diff",
  ).catch((error) => renderDiffCard({ detail: error.message }, "Goose Policy Diff"));
});

dom.compareGooseCertButton.addEventListener("click", () => {
  if (!dom.compareGooseCertLeft.value || !dom.compareGooseCertRight.value) {
    renderDiffCard({ detail: "Choose two certification artifacts first." }, "Goose Certification Diff");
    return;
  }
  loadDiff(
    `/ops/brain/extensions/certifications/compare?left_artifact_id=${encodeURIComponent(dom.compareGooseCertLeft.value)}&right_artifact_id=${encodeURIComponent(dom.compareGooseCertRight.value)}`,
    "Goose Certification Diff",
  ).catch((error) => renderDiffCard({ detail: error.message }, "Goose Certification Diff"));
});

dom.compareGooseAdversaryButton.addEventListener("click", () => {
  if (!dom.compareGooseAdversaryLeft.value || !dom.compareGooseAdversaryRight.value) {
    renderDiffCard({ detail: "Choose two adversary reviews first." }, "Goose Adversary Diff");
    return;
  }
  loadDiff(
    `/ops/brain/security/adversary-reviews/compare?left_review_id=${encodeURIComponent(dom.compareGooseAdversaryLeft.value)}&right_review_id=${encodeURIComponent(dom.compareGooseAdversaryRight.value)}`,
    "Goose Adversary Diff",
  ).catch((error) => renderDiffCard({ detail: error.message }, "Goose Adversary Diff"));
});

dom.compareGooseAcpButton.addEventListener("click", () => {
  if (!dom.compareGooseAcpLeft.value || !dom.compareGooseAcpRight.value) {
    renderDiffCard({ detail: "Choose two ACP provider reports first." }, "Goose ACP Diff");
    return;
  }
  loadDiff(
    `/ops/brain/acp/providers/compare?left_provider_id=${encodeURIComponent(dom.compareGooseAcpLeft.value)}&right_provider_id=${encodeURIComponent(dom.compareGooseAcpRight.value)}`,
    "Goose ACP Diff",
  ).catch((error) => renderDiffCard({ detail: error.message }, "Goose ACP Diff"));
});

dom.compareFleetButton.addEventListener("click", () => {
  if (!dom.compareFleetId.value || !dom.compareFleetWindowLeft.value || !dom.compareFleetWindowRight.value) {
    renderDiffCard({ detail: "Choose a fleet and two cohort windows first." }, "Cohort Window Diff");
    return;
  }
  const subject = dom.filterSubject.value || "";
  loadDiff(
    `/ops/brain/teachers/cohorts/compare?fleet_id=${encodeURIComponent(dom.compareFleetId.value)}&subject=${encodeURIComponent(subject)}&left_window=${encodeURIComponent(dom.compareFleetWindowLeft.value)}&right_window=${encodeURIComponent(dom.compareFleetWindowRight.value)}`,
    "Cohort Window Diff",
  ).catch((error) => renderDiffCard({ detail: error.message }, "Cohort Window Diff"));
});

dom.clearDiffButton.addEventListener("click", () => {
  renderDiffCard(null, "Diff");
  updateActiveClasses();
  renderOperatorCard();
});

dom.compareReplayButton.addEventListener("click", () => {
  const current = state.replay.frames?.[state.replay.index];
  const anchor = state.replay.frames?.[state.replay.anchorIndex];
  renderDiffCard(buildReplayDiffPayload(anchor, current, "Replay Frame Diff"), "Replay Frame Diff");
});

dom.compareNowThenButton.addEventListener("click", () => {
  const current = state.replay.frames?.[state.replay.index];
  const liveOverlay = state.overlay?.overlay_state;
  if (!current || !liveOverlay) {
    renderDiffCard({ detail: "Live vs frame comparison requires an active frame." }, "Live vs Frame Diff");
    return;
  }
  renderDiffCard(
    {
      left: { frame_id: "live-overlay", subject: liveOverlay.route_activity?.selected_expert || liveOverlay.active_subjects?.[0], lineage: liveOverlay.dream_activity?.dream_lineage || "live-derived" },
      right: { frame_id: current.frame_id, subject: current.selected_expert, lineage: current.lineage },
      scene_delta: {
        hot_subjects: computeReplaySubjectDelta(
          { link_activity: liveOverlay.link_activity || {}, active_subjects: liveOverlay.active_subjects || [] },
          { link_activity: current.overlay?.link_activity || {}, active_subjects: current.overlay?.active_subjects || [] },
        ),
        hot_links: computeReplayLinkDelta(
          { link_activity: liveOverlay.link_activity || {}, active_subjects: liveOverlay.active_subjects || [] },
          { link_activity: current.overlay?.link_activity || {}, active_subjects: current.overlay?.active_subjects || [] },
        ),
      },
      diff: {
        live_trace_id: liveOverlay.route_activity?.trace_id,
        frame_id: current.frame_id,
        live_registry_layer: liveOverlay.active_registry_layer,
        frame_lineage: current.lineage,
      },
    },
    "Live vs Frame Diff",
  );
});

dom.gooseCompareGroupFilters?.addEventListener("change", (event) => {
  const target = event.target;
  if (!(target instanceof HTMLInputElement) || target.dataset.gooseGroupFilter === undefined) {
    return;
  }
  const selectedGroups = [...dom.gooseCompareGroupFilters.querySelectorAll("input[data-goose-group-filter]:checked")]
    .map((input) => input.dataset.gooseGroupFilter)
    .filter((value) => value && state.gooseCompare.availableGroups.includes(value));
  state.gooseCompare.selectedGroups = selectedGroups.length ? selectedGroups : state.gooseCompare.availableGroups.slice();
  rerenderActiveDiffCard();
});

dom.gooseCompareExpandAllButton?.addEventListener("click", () => {
  state.gooseCompare.collapseMode = "expand-all";
  rerenderActiveDiffCard();
});

dom.gooseCompareCollapseAllButton?.addEventListener("click", () => {
  state.gooseCompare.collapseMode = "collapse-all";
  rerenderActiveDiffCard();
});

dom.gooseCompareResetFiltersButton?.addEventListener("click", () => {
  state.gooseCompare.selectedGroups = state.gooseCompare.availableGroups.slice();
  state.gooseCompare.collapseMode = (gooseCompareControlCatalog().default_expanded_groups || []).length
    ? "default-expanded"
    : "focus-first";
  rerenderActiveDiffCard();
});

dom.toggleDepthView.addEventListener("change", () => {
  renderDepthInspection();
  renderOperatorCard();
});

dom.toggleLowPower.addEventListener("change", () => {
  state.performance.lowPower = Boolean(dom.toggleLowPower.checked);
  renderLivePosture();
  renderOperatorCard();
  renderReplayTimeline();
  renderDepthInspection();
});

dom.timelineCard.addEventListener("click", (event) => {
  const actionTarget = event.target.closest("[data-frame-action]");
  if (!actionTarget) {
    return;
  }
  const index = Number(actionTarget.dataset.replayIndex || -1);
  if (index < 0 || index >= (state.replay.frames?.length || 0)) {
    return;
  }
  if (actionTarget.dataset.frameAction === "anchor") {
    state.replay.anchorIndex = index;
    dom.replayAnchorRange.value = String(index);
  } else {
    state.replay.index = index;
    state.replay.enabled = true;
    dom.replayRange.value = String(index);
  }
  renderReplayStatus();
  renderReplayTimeline();
  updateActiveClasses();
  renderLivePosture();
  renderEvidenceCards();
  renderOperatorCard();
});

document.addEventListener("visibilitychange", () => {
  state.performance.pageHidden = document.hidden;
  if (document.hidden) {
    clearInterval(state.replayTimer);
    cancelAnimationFrame(state.animationHandle);
    state.replay.playing = false;
    dom.toggleReplayButton.textContent = "Play Replay";
  } else {
    cancelAnimationFrame(state.animationHandle);
    drawAmbientFrame(performance.now());
  }
  renderLivePosture();
  renderOperatorCard();
});

dom.sceneSvg.addEventListener("wheel", (event) => {
  event.preventDefault();
  const scale = event.deltaY > 0 ? 1.08 : 0.92;
  const rect = dom.sceneSvg.getBoundingClientRect();
  const mx = ((event.clientX - rect.left) / rect.width) * state.viewBox.w + state.viewBox.x;
  const my = ((event.clientY - rect.top) / rect.height) * state.viewBox.h + state.viewBox.y;
  const nextW = Math.max(240, Math.min(3000, state.viewBox.w * scale));
  const nextH = Math.max(220, Math.min(2200, state.viewBox.h * scale));
  state.viewBox = {
    x: mx - ((mx - state.viewBox.x) * (nextW / state.viewBox.w)),
    y: my - ((my - state.viewBox.y) * (nextH / state.viewBox.h)),
    w: nextW,
    h: nextH,
  };
  applyViewBox();
});

dom.sceneSvg.addEventListener("pointerdown", (event) => {
  dom.sceneSvg.classList.add("dragging");
  dom.sceneSvg.setPointerCapture(event.pointerId);
  state.drag = { x: event.clientX, y: event.clientY, start: { ...state.viewBox } };
});

dom.sceneSvg.addEventListener("pointermove", (event) => {
  if (!state.drag) {
    return;
  }
  const rect = dom.sceneSvg.getBoundingClientRect();
  const dx = ((event.clientX - state.drag.x) / rect.width) * state.drag.start.w;
  const dy = ((event.clientY - state.drag.y) / rect.height) * state.drag.start.h;
  state.viewBox = {
    x: state.drag.start.x - dx,
    y: state.drag.start.y - dy,
    w: state.drag.start.w,
    h: state.drag.start.h,
  };
  applyViewBox();
});

function endDrag(event) {
  if (state.drag) {
    dom.sceneSvg.releasePointerCapture?.(event.pointerId);
  }
  state.drag = null;
  dom.sceneSvg.classList.remove("dragging");
}

dom.sceneSvg.addEventListener("pointerup", endDrag);
dom.sceneSvg.addEventListener("pointerleave", endDrag);

bootstrap().catch((error) => {
  dom.sceneStatus.textContent = `Visualizer bootstrap failed: ${error.message}`;
});
