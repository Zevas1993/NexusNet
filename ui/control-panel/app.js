const dom = {
  connectionDot: document.getElementById("connectionDot"),
  connectionText: document.getElementById("connectionText"),
  sessionInput: document.getElementById("sessionInput"),
  refreshButton: document.getElementById("refreshButton"),
  runtimeAccelerationMode: document.getElementById("runtimeAccelerationMode"),
  runtimeAccelerationApply: document.getElementById("runtimeAccelerationApply"),
  runtimeAccelerationStatus: document.getElementById("runtimeAccelerationStatus"),
  canonCommandForm: document.getElementById("canonCommandForm"),
  canonCommandInput: document.getElementById("canonCommandInput"),
  canonCommandPriority: document.getElementById("canonCommandPriority"),
  canonCommandButton: document.getElementById("canonCommandButton"),
  canonCommandStatus: document.getElementById("canonCommandStatus"),
  canonRealizationLedger: document.getElementById("canonRealizationLedger"),
  canonCompletionMatrix: document.getElementById("canonCompletionMatrix"),
  completionPercent: document.getElementById("completionPercent"),
  completionState: document.getElementById("completionState"),
  completionScope: document.getElementById("completionScope"),
  evolutionDossier: document.getElementById("evolutionDossier"),
  pageNav: document.getElementById("pageNav"),
  activeTitle: document.getElementById("activeTitle"),
  stateLegend: document.getElementById("stateLegend"),
  gateGrid: document.getElementById("gateGrid"),
  pageTitle: document.getElementById("pageTitle"),
  pageState: document.getElementById("pageState"),
  pageSummary: document.getElementById("pageSummary"),
  metricGrid: document.getElementById("metricGrid"),
  requiredList: document.getElementById("requiredList"),
  complianceList: document.getElementById("complianceList"),
  realizeSurfaceButton: document.getElementById("realizeSurfaceButton"),
  realizeSurfaceStatus: document.getElementById("realizeSurfaceStatus"),
  surfaceDrilldownList: document.getElementById("surfaceDrilldownList"),
  canonProofForm: document.getElementById("canonProofForm"),
  canonProofQuestion: document.getElementById("canonProofQuestion"),
  canonProofActor: document.getElementById("canonProofActor"),
  canonProofDetail: document.getElementById("canonProofDetail"),
  canonProofButton: document.getElementById("canonProofButton"),
  canonProofStatus: document.getElementById("canonProofStatus"),
  answerLinkGrid: document.getElementById("answerLinkGrid"),
  evidenceList: document.getElementById("evidenceList"),
  radarList: document.getElementById("radarList"),
  runtimeScorecard: document.getElementById("runtimeScorecard"),
  protocolTrustScorecard: document.getElementById("protocolTrustScorecard"),
  protocolTrustRegistryScorecard: document.getElementById("protocolTrustRegistryScorecard"),
  selfImprovementScorecard: document.getElementById("selfImprovementScorecard"),
  developmentalCortexScorecard: document.getElementById("developmentalCortexScorecard"),
  selfReviewScorecard: document.getElementById("selfReviewScorecard"),
  communicationIntegrationScorecard: document.getElementById("communicationIntegrationScorecard"),
  inputIngestionScorecard: document.getElementById("inputIngestionScorecard"),
  liveFlowScorecard: document.getElementById("liveFlowScorecard"),
  neuralCoreScorecard: document.getElementById("neuralCoreScorecard"),
  observabilityScorecard: document.getElementById("observabilityScorecard"),
  genAIObservabilityScorecard: document.getElementById("genAIObservabilityScorecard"),
  securityGovernanceScorecard: document.getElementById("securityGovernanceScorecard"),
  policyKernelScorecard: document.getElementById("policyKernelScorecard"),
  agenticPipelineScorecard: document.getElementById("agenticPipelineScorecard"),
  agentOpportunityScorecard: document.getElementById("agentOpportunityScorecard"),
  harnessProviderScorecard: document.getElementById("harnessProviderScorecard"),
  harnessRoutingScorecard: document.getElementById("harnessRoutingScorecard"),
  harnessImprovementLedger: document.getElementById("harnessImprovementLedger"),
  edgeWorkloadRouterScorecard: document.getElementById("edgeWorkloadRouterScorecard"),
  multimodalComputerUseScorecard: document.getElementById("multimodalComputerUseScorecard"),
  inferenceEconomyRouterScorecard: document.getElementById("inferenceEconomyRouterScorecard"),
  inferenceArchitectureScorecard: document.getElementById("inferenceArchitectureScorecard"),
  cacheLedgerScorecard: document.getElementById("cacheLedgerScorecard"),
  runtimeWorkloadScorecards: document.getElementById("runtimeWorkloadScorecards"),
  quantizationCatalogScorecard: document.getElementById("quantizationCatalogScorecard"),
  browserContextScorecard: document.getElementById("browserContextScorecard"),
  engramMemoryScorecard: document.getElementById("engramMemoryScorecard"),
  datasetRadarScorecard: document.getElementById("datasetRadarScorecard"),
  datasetRadarRefreshForm: document.getElementById("datasetRadarRefreshForm"),
  datasetRadarPreset: document.getElementById("datasetRadarPreset"),
  datasetRadarQuery: document.getElementById("datasetRadarQuery"),
  datasetRadarSort: document.getElementById("datasetRadarSort"),
  datasetRadarLimit: document.getElementById("datasetRadarLimit"),
  datasetRadarRequiredTags: document.getElementById("datasetRadarRequiredTags"),
  datasetRadarBlockedTags: document.getElementById("datasetRadarBlockedTags"),
  datasetRadarAuthors: document.getElementById("datasetRadarAuthors"),
  datasetRadarSourceFamilyFilter: document.getElementById("datasetRadarSourceFamilyFilter"),
  datasetRadarRefreshButton: document.getElementById("datasetRadarRefreshButton"),
  datasetRadarBatchButton: document.getElementById("datasetRadarBatchButton"),
  datasetRadarRefreshStatus: document.getElementById("datasetRadarRefreshStatus"),
  datasetRadarCandidateReviewForm: document.getElementById("datasetRadarCandidateReviewForm"),
  datasetRadarReviewDatasetId: document.getElementById("datasetRadarReviewDatasetId"),
  datasetRadarReviewState: document.getElementById("datasetRadarReviewState"),
  datasetRadarReviewReason: document.getElementById("datasetRadarReviewReason"),
  datasetRadarCandidateReviewButton: document.getElementById("datasetRadarCandidateReviewButton"),
  datasetRadarMaterialRequestForm: document.getElementById("datasetRadarMaterialRequestForm"),
  datasetRadarMaterialTarget: document.getElementById("datasetRadarMaterialTarget"),
  datasetRadarMaterialTeacher: document.getElementById("datasetRadarMaterialTeacher"),
  datasetRadarMaterialSplit: document.getElementById("datasetRadarMaterialSplit"),
  datasetRadarMaterialLimit: document.getElementById("datasetRadarMaterialLimit"),
  datasetRadarMaterialRequestButton: document.getElementById("datasetRadarMaterialRequestButton"),
  datasetRadarSourceDetailForm: document.getElementById("datasetRadarSourceDetailForm"),
  datasetRadarSourceDetailDatasetId: document.getElementById("datasetRadarSourceDetailDatasetId"),
  datasetRadarSourceDetailButton: document.getElementById("datasetRadarSourceDetailButton"),
  datasetForgeManifestForm: document.getElementById("datasetForgeManifestForm"),
  datasetForgeManifestId: document.getElementById("datasetForgeManifestId"),
  datasetForgePurpose: document.getElementById("datasetForgePurpose"),
  datasetForgeMaterialRequestRef: document.getElementById("datasetForgeMaterialRequestRef"),
  datasetForgeTaskType: document.getElementById("datasetForgeTaskType"),
  datasetForgeSourceId: document.getElementById("datasetForgeSourceId"),
  datasetForgeRadarSourceId: document.getElementById("datasetForgeRadarSourceId"),
  datasetForgeIntendedSplit: document.getElementById("datasetForgeIntendedSplit"),
  datasetForgeApplyHandoffButton: document.getElementById("datasetForgeApplyHandoffButton"),
  datasetForgeSourceText: document.getElementById("datasetForgeSourceText"),
  datasetForgeOperatorApproved: document.getElementById("datasetForgeOperatorApproved"),
  datasetForgeManifestButton: document.getElementById("datasetForgeManifestButton"),
  datasetForgeManifestStatus: document.getElementById("datasetForgeManifestStatus"),
  datasetForgeScorecard: document.getElementById("datasetForgeScorecard"),
  knowledgeArtifactsScorecard: document.getElementById("knowledgeArtifactsScorecard"),
  adapterRegistryScorecard: document.getElementById("adapterRegistryScorecard"),
  fineTuneDecisionGateScorecard: document.getElementById("fineTuneDecisionGateScorecard"),
  adapterTrainingScorecard: document.getElementById("adapterTrainingScorecard"),
  growthEngineScorecard: document.getElementById("growthEngineScorecard"),
  productionSpineScorecard: document.getElementById("productionSpineScorecard"),
  evalRegistryScorecard: document.getElementById("evalRegistryScorecard"),
  artifactTrustRegistryScorecard: document.getElementById("artifactTrustRegistryScorecard"),
  autonomousUpdatesScorecard: document.getElementById("autonomousUpdatesScorecard"),
  blackBoxRecorder: document.getElementById("blackBoxRecorder"),
  hiveConsensusScorecard: document.getElementById("hiveConsensusScorecard"),
  aoHiveScorecard: document.getElementById("aoHiveScorecard"),
  expertsHiveScorecard: document.getElementById("expertsHiveScorecard"),
  researcherSwarmScorecard: document.getElementById("researcherSwarmScorecard"),
  forwardRadarScorecard: document.getElementById("forwardRadarScorecard"),
  evalSuiteScorecard: document.getElementById("evalSuiteScorecard"),
  memoryProvenanceScorecard: document.getElementById("memoryProvenanceScorecard"),
  memoryQualityScorecard: document.getElementById("memoryQualityScorecard"),
  artifactTrustScorecard: document.getElementById("artifactTrustScorecard"),
  hardwareMatrixScorecard: document.getElementById("hardwareMatrixScorecard"),
  visualOpsScorecard: document.getElementById("visualOpsScorecard"),
  toolExecutionScorecard: document.getElementById("toolExecutionScorecard"),
  assimilationTargetScorecard: document.getElementById("assimilationTargetScorecard"),
  videoAssimilationScorecard: document.getElementById("videoAssimilationScorecard"),
  retrievalPlannerScorecard: document.getElementById("retrievalPlannerScorecard"),
  operatorEventsScorecard: document.getElementById("operatorEventsScorecard"),
  conceptTelemetryScorecard: document.getElementById("conceptTelemetryScorecard"),
  hiveNeuralSubstrateScorecard: document.getElementById("hiveNeuralSubstrateScorecard"),
  sandboxAgentFactoryScorecard: document.getElementById("sandboxAgentFactoryScorecard"),
  outputDeliveryScorecard: document.getElementById("outputDeliveryScorecard"),
  quantCatalog: document.getElementById("quantCatalog"),
  sourceDocs: document.getElementById("sourceDocs"),
  memoryGrid: document.getElementById("memoryGrid"),
  evolutionGrid: document.getElementById("evolutionGrid"),
  orchestratorStrip: document.getElementById("orchestratorStrip"),
  aoHiveStrip: document.getElementById("aoHiveStrip"),
  coreMetrics: document.getElementById("coreMetrics"),
  executionStrip: document.getElementById("executionStrip"),
  buildStrip: document.getElementById("buildStrip"),
  outputStrip: document.getElementById("outputStrip"),
  expertGrid: document.getElementById("expertGrid"),
  securityGrid: document.getElementById("securityGrid"),
  commsGrid: document.getElementById("commsGrid"),
  systemPrinciples: document.getElementById("systemPrinciples"),
  hiveCommandChain: document.getElementById("hiveCommandChain"),
  hiveCommandChainDetail: document.getElementById("hiveCommandChainDetail"),
  hiveTraitGrid: document.getElementById("hiveTraitGrid"),
  hiveSignalGrid: document.getElementById("hiveSignalGrid"),
  miniBrainGrid: document.getElementById("miniBrainGrid"),
  cockpitModeTabs: document.getElementById("cockpitModeTabs"),
  cockpitCommandActions: document.getElementById("cockpitCommandActions"),
  cockpitCommandChain: document.getElementById("cockpitCommandChain"),
  cockpitStats: document.getElementById("cockpitStats"),
  cockpitOperationsBoard: document.getElementById("cockpitOperationsBoard"),
  cockpitAlertRail: document.getElementById("cockpitAlertRail"),
  cockpitGateMini: document.getElementById("cockpitGateMini"),
  cockpitTimeline: document.getElementById("cockpitTimeline"),
  inputGrid: document.getElementById("inputGrid"),
};

const state = {
  payload: null,
  controlPanel: null,
  completion: null,
  runtimeScorecard: null,
  evolutionDossier: null,
  selfImprovement: null,
  selfReview: null,
  protocolTrust: null,
  protocolTrustRegistry: null,
  communicationIntegration: null,
  inputIngestion: null,
  liveFlow: null,
  neuralCore: null,
  observability: null,
  genAIObservability: null,
  securityGovernance: null,
  policyKernel: null,
  agenticPipeline: null,
  agentOpportunity: null,
  harnessProvider: null,
  harnessRouting: null,
  harnessImprovementLedger: null,
  edgeWorkloadRouter: null,
  multimodalComputerUse: null,
  inferenceEconomyRouter: null,
  inferenceArchitecture: null,
  cacheLedger: null,
  runtimeWorkloadScorecards: null,
  quantizationCatalogScorecard: null,
  browserContext: null,
  engramMemory: null,
  datasetRadar: null,
  datasetRadarRefresh: null,
  datasetRadarBatch: null,
  datasetRadarCandidateReview: null,
  datasetRadarMaterialRequest: null,
  datasetRadarSourceDetail: null,
  datasetForge: null,
  datasetForgeManifest: null,
  knowledgeArtifacts: null,
  knowledgeArtifactTrustScan: null,
  adapterRegistry: null,
  fineTuneDecisionGate: null,
  adapterTraining: null,
  growthEngine: null,
  productionSpine: null,
  evalRegistry: null,
  artifactTrustRegistry: null,
  autonomousUpdates: null,
  releaseWrapperStatus: null,
  releaseWrapperLastAction: null,
  releaseWrapperRuntime: null,
  releaseHarnessRuntime: null,
  cluster9TeacherReconciliation: null,
  releaseWrapperReadiness: null,
  releaseWrapperTelemetry: null,
  releaseWrapperSessionLifecycle: null,
  blackBox: null,
  hiveConsensus: null,
  aoHive: null,
  expertsHive: null,
  researcherSwarm: null,
  forwardRadar: null,
  evalSuite: null,
  memoryProvenance: null,
  memoryQuality: null,
  artifactTrust: null,
  hardwareMatrix: null,
  visualOps: null,
  toolExecution: null,
  assimilationTargets: null,
  videoAssimilation: null,
  retrievalPlanner: null,
  operatorEvents: null,
  conceptTelemetry: null,
  hiveNeuralSubstrate: null,
  hiveNeuralSubstrateReplay: null,
  sandboxAgentFactory: null,
  outputDelivery: null,
  surfaceDrilldown: null,
  currentPageId: "overview",
};

const canonScorecardEndpoints = {
  completion: "/ops/brain/canon/completion",
  runtimeScorecard: "/ops/brain/canon/runtime-scorecard",
  evolutionDossier: "/ops/brain/canon/evolution-dossier",
  selfImprovement: "/ops/brain/canon/self-improvement",
  selfReview: "/ops/brain/canon/self-review",
  protocolTrust: "/ops/brain/canon/protocol-trust",
  protocolTrustRegistry: "/ops/brain/canon/protocol-trust-registry",
  communicationIntegration: "/ops/brain/canon/communication-integration",
  inputIngestion: "/ops/brain/canon/input-ingestion",
  liveFlow: "/ops/brain/canon/live-flow",
  neuralCore: "/ops/brain/canon/neural-core",
  observability: "/ops/brain/canon/observability",
  genAIObservability: "/ops/brain/canon/genai-observability",
  securityGovernance: "/ops/brain/canon/security-governance",
  policyKernel: "/ops/brain/canon/policy-kernel",
  agenticPipeline: "/ops/brain/canon/agentic-pipelines",
  agentOpportunity: "/ops/brain/canon/agent-opportunities",
  harnessProvider: "/ops/brain/canon/harness-providers",
  harnessRouting: "/ops/brain/canon/harness-routing",
  harnessImprovementLedger: "/ops/brain/canon/harness-ledger",
  edgeWorkloadRouter: "/ops/brain/canon/edge-workload-router",
  multimodalComputerUse: "/ops/brain/canon/multimodal-computer-use",
  inferenceEconomyRouter: "/ops/brain/canon/inference-economy-router",
  inferenceArchitecture: "/ops/brain/canon/inference-architecture",
  cacheLedger: "/ops/brain/canon/cache-ledger",
  runtimeWorkloadScorecards: "/ops/brain/canon/runtime-scorecards",
  quantizationCatalogScorecard: "/ops/brain/canon/quantization-catalog",
  browserContext: "/ops/brain/canon/browser-context",
  engramMemory: "/ops/brain/canon/engram-memory",
  datasetRadar: "/ops/brain/canon/dataset-radar",
  datasetRadarRefreshPresets: "/ops/brain/dataset-radar/refresh-presets",
  datasetRadarRefreshBatch: "/ops/brain/dataset-radar/refresh-batch",
  datasetRadarCandidateReview: "/ops/brain/dataset-radar/candidate-review",
  datasetRadarMaterialRequest: "/ops/brain/dataset-radar/material-request",
  datasetRadarSourceDetail: "/ops/brain/dataset-radar/sources",
  datasetForge: "/ops/brain/canon/dataset-forge",
  datasetForgeManifestBuild: "/ops/brain/dataset-forge/manifests",
  knowledgeArtifacts: "/ops/brain/canon/knowledge-artifacts",
  adapterRegistry: "/ops/brain/canon/adapter-registry",
  fineTuneDecisionGate: "/ops/brain/canon/fine-tune-decision-gate",
  adapterTraining: "/ops/brain/canon/adapter-training",
  growthEngine: "/ops/brain/canon/growth-engine",
  productionSpine: "/ops/brain/canon/production-spine",
  evalRegistry: "/ops/brain/canon/eval-registry",
  artifactTrustRegistry: "/ops/brain/canon/artifact-trust-registry",
  autonomousUpdates: "/ops/brain/canon/autonomous-updates",
  blackBox: "/ops/brain/canon/blackbox",
  hiveConsensus: "/ops/brain/canon/hive-consensus",
  aoHive: "/ops/brain/canon/ao-hive",
  expertsHive: "/ops/brain/canon/experts-hive",
  researcherSwarm: "/ops/brain/canon/researcher-swarm",
  forwardRadar: "/ops/brain/canon/forward-radar",
  evalSuite: "/ops/brain/canon/eval-suite",
  memoryProvenance: "/ops/brain/canon/memory-provenance",
  memoryQuality: "/ops/brain/canon/memory-quality",
  artifactTrust: "/ops/brain/canon/artifact-trust",
  hardwareMatrix: "/ops/brain/canon/hardware-matrix",
  visualOps: "/ops/brain/canon/visualops",
  toolExecution: "/ops/brain/canon/tool-execution",
  assimilationTargets: "/ops/brain/canon/assimilation-targets",
  videoAssimilation: "/ops/brain/canon/video-assimilation-targets",
  retrievalPlanner: "/ops/brain/retrieval/planner",
  operatorEvents: "/ops/brain/operator-events",
  conceptTelemetry: "/ops/brain/concept-telemetry",
  hiveNeuralSubstrate: "/ops/brain/canon/hive-substrate",
  hiveNeuralSubstrateReplay: "/ops/brain/hive-substrate/replay",
  hiveNeuralSnapshot: "/ops/brain/canon/hive-neural-snapshot",
  sandboxAgentFactory: "/ops/brain/canon/sandbox-agent-factory",
  outputDelivery: "/ops/brain/canon/output-delivery",
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

function escapeAttr(value) {
  return escapeHtml(value)
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function pretty(value) {
  return String(value || "")
    .replaceAll("_", " ")
    .replaceAll("-", " ")
    .replace(/\s+/g, " ")
    .trim();
}

function valueText(value) {
  if (value === null || value === undefined || value === "") {
    return "unknown";
  }
  if (typeof value === "boolean") {
    return value ? "true" : "false";
  }
  if (Array.isArray(value)) {
    return value.length ? value.join(", ") : "none";
  }
  if (typeof value === "object") {
    const entries = Object.entries(value)
      .filter(([, entryValue]) => entryValue !== null && entryValue !== undefined && entryValue !== "")
      .slice(0, 5);
    if (!entries.length) {
      return "none";
    }
    return entries.map(([key, entryValue]) => `${key}: ${valueText(entryValue)}`).join(" | ");
  }
  return String(value);
}

function inputList(value) {
  return String(value || "")
    .split(/[,\s]+/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function datasetRadarDiscoveryFilters() {
  const filters = {};
  const requiredTags = inputList(dom.datasetRadarRequiredTags?.value);
  const blockedTags = inputList(dom.datasetRadarBlockedTags?.value);
  const authors = inputList(dom.datasetRadarAuthors?.value);
  const sourceFamily = (dom.datasetRadarSourceFamilyFilter?.value || "").trim();
  if (requiredTags.length) {
    filters.required_tags = requiredTags;
  }
  if (blockedTags.length) {
    filters.blocked_tags = blockedTags;
  }
  if (authors.length) {
    filters.authors = authors;
  }
  if (sourceFamily) {
    filters.source_families = [sourceFamily];
  }
  return filters;
}

function latestDatasetForgeHandoff() {
  const sourceDetailUsage = state.datasetRadarSourceDetail?.material_request_usage || [];
  return state.datasetRadarMaterialRequest?.dataset_forge_handoff
    || sourceDetailUsage.find((usage) => usage.dataset_forge_handoff?.endpoint)?.dataset_forge_handoff
    || state.datasetRadar?.latest_material_request?.dataset_forge_handoff
    || {};
}

function applyDatasetForgeHandoffTemplate(event) {
  event?.preventDefault?.();
  const handoff = latestDatasetForgeHandoff();
  const template = handoff.request_body_template || {};
  const source = (template.sources || [])[0] || {};
  if (!handoff.endpoint || !Object.keys(template).length) {
    dom.datasetForgeManifestStatus.textContent = "No Dataset Radar handoff is available yet. Request material through Dataset Radar first.";
    return;
  }
  dom.datasetForgeManifestId.value = template.dataset_manifest_id || "";
  dom.datasetForgePurpose.value = template.purpose || "";
  dom.datasetForgeMaterialRequestRef.value = template.material_request_ref || "";
  dom.datasetForgeTaskType.value = template.task_type || "tool_use";
  dom.datasetForgeSourceId.value = source.source_id || "";
  dom.datasetForgeRadarSourceId.value = source.dataset_radar_source_id || source.source_id || "";
  dom.datasetForgeIntendedSplit.value = source.metadata?.intended_split || template.metadata?.requested_split || "teacher_context";
  dom.datasetForgeSourceText.value = "";
  dom.datasetForgeOperatorApproved.checked = false;
  dom.datasetForgeManifestStatus.textContent = `${handoff.handoff_rule || "Operator-reviewed excerpt required."} Paste the reviewed excerpt before building.`;
}

function datasetForgeManifestRequestBody() {
  const manifestId = (dom.datasetForgeManifestId?.value || "").trim();
  const purpose = (dom.datasetForgePurpose?.value || "").trim();
  const materialRequestRef = (dom.datasetForgeMaterialRequestRef?.value || "").trim();
  const sourceId = (dom.datasetForgeSourceId?.value || "").trim();
  const radarSourceId = (dom.datasetForgeRadarSourceId?.value || "").trim();
  const sourceText = (dom.datasetForgeSourceText?.value || "").trim();
  const intendedSplit = dom.datasetForgeIntendedSplit?.value || "teacher_context";
  const taskType = dom.datasetForgeTaskType?.value || "tool_use";
  const operatorApproved = Boolean(dom.datasetForgeOperatorApproved?.checked);
  if (!manifestId || !purpose || !sourceId || !sourceText) {
    throw new Error("DatasetForge manifest id, purpose, source id, and reviewed excerpt are required.");
  }
  if (!operatorApproved) {
    throw new Error("Operator approval is required before building a DatasetForge manifest.");
  }
  if (/operator-reviewed excerpt placeholder/i.test(sourceText)) {
    throw new Error("Replace the Dataset Radar placeholder with an operator-reviewed excerpt before building.");
  }
  return {
    dataset_manifest_id: manifestId,
    purpose,
    material_request_ref: materialRequestRef || null,
    task_type: taskType,
    operator_approved: operatorApproved,
    metadata: {
      source: "control-panel-dataset-forge-form",
      intended_split: intendedSplit,
      handoff_endpoint: latestDatasetForgeHandoff().endpoint || null,
      no_training_execution_authorized: true,
    },
    sources: [
      {
        source_id: sourceId,
        source_type: "web",
        text: sourceText,
        license_status: "approved",
        contains_private_data: false,
        provenance_ref: materialRequestRef ? `dataset-radar:${materialRequestRef}:${radarSourceId || sourceId}` : `control-panel:${sourceId}`,
        dataset_radar_source_id: radarSourceId || null,
        allowed_distillation_state: "not_applicable",
        contamination_risk: "unknown",
        metadata: {
          material_request_ref: materialRequestRef || null,
          intended_split: intendedSplit,
          operator_reviewed_excerpt: true,
          training_execution_authorized: false,
        },
      },
    ],
  };
}

async function fetchJSON(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(await response.text() || response.statusText);
  }
  return response.json();
}

function setConnection(status, text) {
  dom.connectionDot.className = `dot ${status}`;
  dom.connectionText.textContent = text;
}

function activePage() {
  const pages = state.controlPanel?.pages || [];
  return pages.find((page) => page.page_id === state.currentPageId) || pages[0] || null;
}

function pageById(pageId) {
  return (state.controlPanel?.pages || []).find((page) => page.page_id === pageId) || null;
}

function fill(element, html) {
  if (element) {
    element.innerHTML = html;
  }
}

function statusFor(pageId, fallback = "static-canon") {
  return pageById(pageId)?.state || fallback;
}

function labelFor(pageId, fallback) {
  return pageById(pageId)?.label || fallback;
}

function nodeHtml(label, stateValue = "static-canon", detail = "") {
  return `
    <div class="node ${escapeHtml(stateValue)}">
      <strong>${escapeHtml(label)}</strong>
      ${detail ? `<small>${escapeHtml(detail)}</small>` : `<small>${escapeHtml(pretty(stateValue))}</small>`}
    </div>
  `;
}

function listItems(items) {
  return items.map((item) => `<span>${escapeHtml(item)}</span>`).join("");
}

function signalLabel(value) {
  return pretty(value).toLowerCase();
}

function renderLegend() {
  const states = state.controlPanel?.state_model || [];
  dom.stateLegend.innerHTML = states
    .map((item) => `<span class="legend-chip ${escapeHtml(item)}">${escapeHtml(pretty(item))}</span>`)
    .join("");
}

function renderNav() {
  const pages = state.controlPanel?.pages || [];
  dom.pageNav.innerHTML = pages
    .map((page) => {
      const active = page.page_id === state.currentPageId ? " active" : "";
      return `
        <button class="nav-button${active}" type="button" data-page-id="${escapeHtml(page.page_id)}">
          <strong>${escapeHtml(page.label)}</strong>
          <small>${escapeHtml(pretty(page.state))}</small>
        </button>
      `;
    })
    .join("");
  dom.pageNav.querySelectorAll("[data-page-id]").forEach((button) => {
    button.addEventListener("click", () => {
      state.currentPageId = button.dataset.pageId;
      renderAll();
      loadSurfaceDrilldown().catch((error) => {
        fill(dom.surfaceDrilldownList, `<div class="ref-row">${escapeHtml(error.message)}</div>`);
      });
    });
  });
}

function renderGates() {
  const gates = state.controlPanel?.build_gates || [];
  dom.gateGrid.innerHTML = gates
    .map((gate) => `
      <div class="gate">
        <strong>${escapeHtml(gate.label)}</strong>
        <span class="state-pill ${escapeHtml(gate.state)}">${escapeHtml(pretty(gate.state))}</span>
        <small>${escapeHtml(gate.evidence_ref || "no evidence ref")}</small>
      </div>
    `)
    .join("");
}

function renderPage() {
  const page = activePage();
  if (!page) {
    dom.pageTitle.textContent = "No Control Panel Payload";
    dom.pageSummary.textContent = "The visualizer overlay did not return a control_panel object.";
    dom.pageState.textContent = "missing";
    dom.metricGrid.innerHTML = "";
    dom.requiredList.innerHTML = "";
    dom.complianceList.innerHTML = "";
    dom.surfaceDrilldownList.innerHTML = "";
    dom.canonProofQuestion.innerHTML = "";
    dom.answerLinkGrid.innerHTML = "";
    dom.evidenceList.innerHTML = "";
    return;
  }

  dom.activeTitle.textContent = page.label;
  dom.pageTitle.textContent = page.label;
  dom.pageSummary.textContent = page.summary || "";
  dom.pageState.className = `state-pill ${page.state || "unknown"}`;
  dom.pageState.textContent = pretty(page.state || "unknown");

  dom.metricGrid.innerHTML = Object.entries(page.metrics || {})
    .map(([key, value]) => `
      <div class="metric">
        <small>${escapeHtml(pretty(key))}</small>
        <strong>${escapeHtml(valueText(value))}</strong>
      </div>
    `)
    .join("");

  dom.requiredList.innerHTML = (page.required_surfaces || [])
    .map((item) => `<span class="token">${escapeHtml(item)}</span>`)
    .join("");

  const realizationSurface = state.controlPanel?.canon_realization?.surfaces?.[page.page_id] || {};
  dom.complianceList.innerHTML = (realizationSurface.compliance_controls || [])
    .map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`)
    .join("") || `<span class="token">base surface mapping</span>`;
  dom.surfaceDrilldownList.innerHTML = `<div class="ref-row">Loading selected surface drilldown...</div>`;

  const answerEntries = Object.entries(state.controlPanel?.canon_realization?.operator_questions || {});
  renderProofQuestionOptions(page, answerEntries);
  dom.answerLinkGrid.innerHTML = answerEntries
    .map(([questionId, item]) => `
      <a href="/ops/brain/canon/answers/${escapeHtml(questionId)}?session_id=${encodeURIComponent(dom.sessionInput.value || sessionId())}" target="_blank" rel="noreferrer">
        <strong>${escapeHtml(pretty(questionId))}</strong>
        <small>${escapeHtml(item.prompt || "")}</small>
      </a>
    `)
    .join("");

  const refs = page.evidence_refs || [];
  dom.evidenceList.innerHTML = refs.length
    ? refs.map((ref) => `<div class="ref-row">${escapeHtml(ref)}</div>`).join("")
    : `<div class="ref-row">No live evidence reference declared.</div>`;
}

function renderProofQuestionOptions(page, answerEntries) {
  const surfaceEntries = answerEntries.filter(([, item]) => item.surface_id === page.page_id);
  const options = surfaceEntries.length ? surfaceEntries : answerEntries.slice(0, 1);
  fill(dom.canonProofQuestion, options
    .map(([questionId, item]) => `
      <option value="${escapeHtml(questionId)}">${escapeHtml(pretty(questionId))} | ${escapeHtml(pretty(item.answer_state || "static-canon"))}</option>
    `)
    .join(""));
  dom.canonProofButton.disabled = options.length === 0;
}

function renderSurfaceDrilldown(payload) {
  state.surfaceDrilldown = payload;
  const surface = payload?.surface || {};
  const gates = payload?.book_gates || [];
  const answers = payload?.answer_links || [];
  const evidenceRefs = payload?.evidence_refs || [];
  fill(dom.surfaceDrilldownList, `
    <div class="ref-row">Surface: ${escapeHtml(surface.label || surface.surface_id || "unknown")}</div>
    <div class="ref-row">Gate: ${escapeHtml(gates.map((gate) => gate.gate_id).join(", ") || "base surface mapping")}</div>
    <div class="ref-row">Answers: ${escapeHtml(answers.map((item) => pretty(item.question_id)).join(", ") || "none")}</div>
    <div class="ref-row">Evidence: ${escapeHtml(evidenceRefs.join(", ") || "none")}</div>
  `);
}

async function loadSurfaceDrilldown() {
  const page = activePage();
  if (!page || !dom.surfaceDrilldownList) {
    return;
  }
  const session = dom.sessionInput.value || sessionId();
  const payload = await fetchJSON(`/ops/brain/canon/surfaces/${encodeURIComponent(page.page_id)}?session_id=${encodeURIComponent(session)}`);
  renderSurfaceDrilldown(payload);
}

function renderRadar() {
  const lanes = state.controlPanel?.research_lanes || [];
  dom.radarList.innerHTML = lanes
    .map((lane) => `
      <div class="lane-row">
        <div class="metric-head">
          <strong>${escapeHtml(lane.label)}</strong>
          <span class="state-pill ${escapeHtml(lane.status)}">${escapeHtml(pretty(lane.status))}</span>
        </div>
        <small>${escapeHtml((lane.watch_items || []).join(", "))}</small>
        <small>${escapeHtml(lane.promotion_gate || "")}</small>
      </div>
    `)
    .join("");
}

function renderQuantCatalog() {
  const catalog = state.controlPanel?.quantization_catalog || {};
  const methods = catalog.method_families || [];
  const formats = catalog.formats || [];
  const fields = catalog.required_fields || [];
  dom.quantCatalog.innerHTML = [
    ...methods.map((item) => `<span class="token">${escapeHtml(item)}</span>`),
    ...formats.map((item) => `<span class="token">${escapeHtml(item)}</span>`),
    ...fields.map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`),
  ].join("");
}

function renderRuntimeScorecard() {
  const scorecard = state.runtimeScorecard || {};
  const controls = Object.entries(scorecard.required_controls || {});
  const lanes = scorecard.inference_architecture_lanes || [];
  const methods = scorecard.method_families || [];
  fill(dom.runtimeScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Method Families</strong>
        <span class="state-pill ${methods.includes("TurboQuant") ? "research-candidate" : "degraded"}">TurboQuant</span>
      </div>
      <div class="token-grid">${methods.slice(0, 12).map((item) => `<span class="token">${escapeHtml(item)}</span>`).join("")}</div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Required Controls</strong>
        <span>${escapeHtml(String(controls.length))}</span>
      </div>
      ${controls.map(([controlId, control]) => `
        <div class="ledger-row">
          <strong>${escapeHtml(pretty(controlId))}</strong>
          <span class="state-pill ${escapeHtml(control.state || "static-canon")}">${escapeHtml(pretty(control.state || "static-canon"))}</span>
          <small>${escapeHtml(control.endpoint || (control.evidence_refs || []).slice(0, 3).join(" | ") || "canon-mapped")}</small>
        </div>
      `).join("")}
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Inference Architecture</strong>
        <span class="state-pill research-candidate">radar</span>
      </div>
      ${lanes.map((lane) => `
        <div class="lane-row">
          <div class="metric-head">
            <strong>${escapeHtml(lane.label)}</strong>
            <span class="state-pill ${escapeHtml(lane.state || "research-candidate")}">${escapeHtml(pretty(lane.state || "research-candidate"))}</span>
          </div>
          <small>${escapeHtml(lane.promotion_gate || "")}</small>
        </div>
      `).join("")}
    </article>
  `);
}

function renderEvolutionDossier() {
  const dossier = state.evolutionDossier || {};
  const pipeline = dossier.pipeline || [];
  fill(dom.evolutionDossier, `
    <article class="evolution-summary-card">
      <div class="metric-head">
        <strong>${escapeHtml(pretty(dossier.operating_mode || "shadow-governed-autonomous-updates"))}</strong>
        <span class="state-pill shadow-only">guarded</span>
      </div>
      <small>Promotion boundary: ${escapeHtml(dossier.promotion_boundary || "no autonomous live promotion")}</small>
      <div class="token-grid">${(dossier.required_promotion_evidence || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
    </article>
    <article class="evolution-pipeline-card">
      ${pipeline.map((stage, index) => `
        <div class="timeline-node">
          <small>${escapeHtml(String(index + 1).padStart(2, "0"))}</small>
          <strong>${escapeHtml(stage.label || pretty(stage.stage_id))}</strong>
          <span>${escapeHtml(stage.actor || "NexusBrain")}</span>
          <span class="state-pill ${escapeHtml(stage.state || "shadow-only")}">${escapeHtml(pretty(stage.state || "shadow-only"))}</span>
        </div>
      `).join("")}
    </article>
  `);
}

function renderSelfImprovementScorecard() {
  const scorecard = state.selfImprovement || {};
  const queue = scorecard.queue_summary || {};
  fill(dom.selfImprovementScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${Number(queue.item_count || 0) ? "live-bound" : "static-canon"}">${escapeHtml(`${queue.item_count || 0} queued`)}</span>
      </div>
      <small>${escapeHtml(scorecard.model_update_boundary || "no weight update without review, verification, and regression gates")}</small>
      <div class="token-grid">${(scorecard.optimization_sequence || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
    </article>
    ${scorecardLaneGrid(scorecard.pipeline_stages || [], "stage_id")}
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderDevelopmentalCortexScorecard() {
  if (!dom.developmentalCortexScorecard) {
    return;
  }
  const scorecard = state.developmentalCortex || {};
  const latestAssessment = scorecard.latest_assessment || {};
  const growthCandidate = latestAssessment.growth_candidate || {};
  const promotionCase = latestAssessment.promotion_case || {};
  fill(dom.developmentalCortexScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Developmental Cortex</strong>
        <span class="state-pill ${scorecard.runtime_state === "degraded" ? "blocked" : "live-bound"}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.authority || "NexusBrain")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(latestAssessment.request_id || "none")}</strong><small>developmental cortex assessment</small></span>
        <span><strong>${escapeHtml(growthCandidate.candidate_id || "none")}</strong><small>developmental growth candidate</small></span>
        <span><strong>${escapeHtml(promotionCase.case_id || "none")}</strong><small>developmental promotion case</small></span>
      </div>
      <div class="completion-scope">Production mutation: ${scorecard.production_mutation_allowed ? "allowed" : "blocked"}</div>
    </article>
    ${scorecardLaneGrid(Object.entries(scorecard.subsurfaces || {}).map(([lane_id, surface]) => ({
      lane_id,
      label: (surface && surface.surface_id) ? surface.surface_id : String(surface),
      state: (surface && surface.runtime_state) ? surface.runtime_state : "mapped",
    })))}
    ${scorecardLaneGrid(developmentalSupportLanes().map((lane) => ({
      lane_id: lane.lane_id,
      label: `${lane.surface_id} | ${lane.metric}`,
      state: lane.runtime_state,
    })))}
  `);
}

function developmentalSupportLanes() {
  const authority = state.authoritySpine || {};
  const evidence = state.evidenceStore || {};
  const evalFed = state.evalFederation || {};
  const tools = state.toolActionHarness || {};
  const runtime = state.runtimeDecisionLedger || {};
  return [
    { lane_id: "authority-spine", surface_id: authority.surface_id || "authority-integrity-spine", runtime_state: authority.runtime_state || "static-canon", metric: `decisions ${authority.decision_count || 0} | blocked ${authority.blocked_count || 0}` },
    { lane_id: "evidence-store", surface_id: evidence.surface_id || "content-addressed-evidence-store", runtime_state: evidence.runtime_state || "static-canon", metric: `records ${evidence.record_count || 0}` },
    { lane_id: "eval-federation", surface_id: evalFed.surface_id || "eval-federation", runtime_state: evalFed.runtime_state || "static-canon", metric: `events ${evalFed.event_count || 0}` },
    { lane_id: "tool-action-harness", surface_id: tools.surface_id || "tool-action-harness", runtime_state: tools.runtime_state || "static-canon", metric: `plans ${tools.plan_count || 0}` },
    { lane_id: "runtime-decision-ledger", surface_id: runtime.surface_id || "runtime-decision-ledger", runtime_state: runtime.runtime_state || "static-canon", metric: `decisions ${runtime.decision_count || 0}` },
  ];
}

function renderSelfReviewScorecard() {
  const scorecard = state.selfReview || {};
  const latest = scorecard.latest_review || {};
  const upstream_eval_gate = latest.upstream_eval_gate || {};
  const upstream_lifecycle_gate = upstream_eval_gate.upstream_lifecycle_gate || {};
  const reviews = scorecard.reviews || [];
  fill(dom.selfReviewScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.review_boundary || "independent review and verifier evidence required")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.review_count || 0)}</strong><small>reviews</small></span>
        <span><strong>${escapeHtml(scorecard.accepted_count || 0)}</strong><small>accepted</small></span>
        <span><strong>${escapeHtml(scorecard.blocked_count || 0)}</strong><small>blocked</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(latest.review_id || scorecard.promotion_boundary || "No self-review records yet")}</div>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Self-review upstream eval gate</strong>
        <span class="state-pill ${upstream_eval_gate.promotion_allowed === false ? "blocked" : "live-bound"}">${upstream_eval_gate.promotion_allowed === false ? "blocked" : "clear"}</span>
      </div>
      <small>${escapeHtml(upstream_eval_gate.source || "upstream eval gate")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(upstream_eval_gate.promotion_allowed === false ? "blocked" : "clear")}</strong><small>upstream eval gate</small></span>
        <span><strong>${escapeHtml(upstream_lifecycle_gate.lifecycle_status || "unknown")}</strong><small>lifecycle</small></span>
        <span><strong>${escapeHtml(upstream_lifecycle_gate.growth_engine_gate_allowed === false ? "blocked" : "clear")}</strong><small>growth</small></span>
        <span><strong>${escapeHtml(upstream_eval_gate.blockers?.length || 0)}</strong><small>blockers</small></span>
      </div>
    </article>
    ${scorecardLaneGrid(reviews.slice(0, 6).map((review) => ({
      lane_id: review.review_id,
      label: `${review.candidate_type || "candidate"} | ${review.target_surface || "surface"} | ${review.review_state || "state"}`,
      state: review.status || "static-canon",
    })))}
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderProtocolTrustScorecard() {
  const scorecard = state.protocolTrust || {};
  const protocols = scorecard.protocols || [];
  fill(dom.protocolTrustScorecard, `
    <div class="scorecard-mini-grid">
      ${protocols.map((protocol) => `
        <article class="runtime-scorecard-card">
          <div class="metric-head">
            <strong>${escapeHtml(protocol.protocol_id)}</strong>
            <span class="state-pill live-bound">${escapeHtml(protocol.authority || "NexusBrain")}</span>
          </div>
          <small>${escapeHtml(protocol.label || "")}</small>
          <div class="token-grid">${(protocol.capabilities || []).map((item) => `<span class="token">${escapeHtml(item)}</span>`).join("")}</div>
        </article>
      `).join("")}
    </div>
    <div class="completion-scope">${escapeHtml(scorecard.promotion_boundary || "protocols-remain-adapters-not-brain-authority")}</div>
  `);
}

function renderProtocolTrustRegistryScorecard() {
  const scorecard = state.protocolTrustRegistry || {};
  const latest = scorecard.latest_adapter || {};
  const adapters = scorecard.adapters || [];
  fill(dom.protocolTrustRegistryScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.protocol_boundary || "protocol adapters remain governed hands")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.adapter_count || 0)}</strong><small>adapters</small></span>
        <span><strong>${escapeHtml(scorecard.trusted_count || 0)}</strong><small>trusted</small></span>
        <span><strong>${escapeHtml(scorecard.blocked_count || 0)}</strong><small>blocked</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(latest.adapter_id || "No protocol adapters registered")}</div>
    ${scorecardLaneGrid(adapters.slice(0, 6).map((adapter) => ({
      lane_id: adapter.adapter_id,
      label: `${adapter.protocol || "protocol"} | ${adapter.trust_envelope?.permissions?.length || 0} permissions | ${adapter.trust_envelope?.complete ? "complete" : "incomplete"}`,
      state: adapter.status || "static-canon",
    })))}
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderCommunicationIntegrationScorecard() {
  const scorecard = state.communicationIntegration || {};
  fill(dom.communicationIntegrationScorecard, `
    ${scorecardLaneGrid(scorecard.integration_lanes || [])}
    <div class="completion-scope">${escapeHtml(scorecard.integration_rule || "external communications require consent, permission, trust envelope, and revocation")}</div>
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderInputIngestionScorecard() {
  const scorecard = state.inputIngestion || {};
  fill(dom.inputIngestionScorecard, `
    ${scorecardLaneGrid(scorecard.input_lanes || [])}
    <div class="completion-scope">${escapeHtml(scorecard.intake_rule || "inputs require permission, freshness, redaction, and command correlation")}</div>
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderLiveFlowScorecard() {
  const scorecard = state.liveFlow || {};
  const segments = scorecard.trace_segments || [];
  fill(dom.liveFlowScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.correlation_model?.authority || "NexusBrain")}</strong>
        <span class="state-pill ${scorecard.active_command_id ? "live-bound" : "static-canon"}">${escapeHtml(scorecard.active_command_id ? "correlated" : "standby")}</span>
      </div>
      <small>${escapeHtml(scorecard.correlation_model?.trace_rule || "route, model, memory, tool, policy, eval, and output share command id")}</small>
      <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
    </article>
    ${scorecardLaneGrid(segments, "segment_id")}
  `);
}

function renderNeuralCoreScorecard() {
  const scorecard = state.neuralCore || {};
  const units = scorecard.orchestrator_units || [];
  fill(dom.neuralCoreScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${scorecard.active_command_id ? "live-bound" : "static-canon"}">${escapeHtml(scorecard.fallback_model?.lock_state || "locked-to-nexusbrain")}</span>
      </div>
      <small>${escapeHtml(scorecard.fallback_model?.fallback_rule || "degrade safely before bypassing NexusBrain")}</small>
      <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
    </article>
    ${scorecardLaneGrid(units, "unit_id")}
  `);
}

function renderObservabilityScorecard() {
  const scorecard = state.observability || {};
  const standards = scorecard.trace_standards || [];
  fill(dom.observabilityScorecard, `
    ${scorecardLaneGrid(standards)}
    <div class="completion-scope">${escapeHtml(scorecard.audit_model?.redaction_rule || "redact-private-inputs-before-export")}</div>
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderGenAIObservabilityScorecard() {
  const scorecard = state.genAIObservability || {};
  const latest = scorecard.latest_trace || {};
  const traces = scorecard.traces || [];
  fill(dom.genAIObservabilityScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.export_boundary || scorecard.stability_opt_in || "OpenTelemetry GenAI metadata export")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.trace_count || 0)}</strong><small>traces</small></span>
        <span><strong>${escapeHtml(scorecard.redacted_count || 0)}</strong><small>redacted</small></span>
        <span><strong>${escapeHtml(scorecard.blocked_count || 0)}</strong><small>blocked</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(latest.span_name || scorecard.stability_opt_in || "No GenAI traces recorded")}</div>
    ${scorecardLaneGrid(traces.slice(0, 6).map((trace) => ({
      lane_id: trace.trace_id,
      label: `${trace.otel_attributes?.["gen_ai.operation.name"] || "operation"} | ${trace.otel_attributes?.["gen_ai.provider.name"] || "provider"} | ${trace.redaction_state || "redaction"}`,
      state: trace.status || "static-canon",
    })))}
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderSecurityGovernanceScorecard() {
  const scorecard = state.securityGovernance || {};
  fill(dom.securityGovernanceScorecard, `
    ${scorecardLaneGrid(scorecard.security_lanes || [])}
    <div class="completion-scope">${escapeHtml(scorecard.security_rule || "security-sensitive actions require policy, audit, privacy, and rollback")}</div>
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderPolicyKernelScorecard() {
  const scorecard = state.policyKernel || {};
  const actions = scorecard.operator_actions || {};
  fill(dom.policyKernelScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.policy_kernel_state || "static-canon")}">${escapeHtml(pretty(scorecard.policy_kernel_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.policy_boundary || "deterministic floor under agentic work")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.default_rule_count || 0)}</strong><small>rules</small></span>
        <span><strong>${escapeHtml((scorecard.rule_families || []).length)}</strong><small>families</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(scorecard.promotion_rule || "policy findings must be resolved or waived before autonomous promotion")}</div>
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
    <div class="token-grid">${Object.entries(actions).map(([action, contract]) => `<span class="token">${escapeHtml(pretty(action))}: ${escapeHtml(contract.endpoint || "")}</span>`).join("")}</div>
  `);
}

function renderAgenticPipelineScorecard() {
  const scorecard = state.agenticPipeline || {};
  const latest = scorecard.latest_run || {};
  const blocks = latest.blocks || [];
  fill(dom.agenticPipelineScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.promotion_boundary || "manifest, events, policy scan, and manager review required")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.run_count || 0)}</strong><small>runs</small></span>
        <span><strong>${escapeHtml(scorecard.blocked_count || 0)}</strong><small>blocked</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(latest.goal || "No active pipeline run yet")}</div>
    ${scorecardLaneGrid(blocks.map((block) => ({
      lane_id: block.block_id,
      label: `${block.role}: ${block.expected_output}`,
      state: block.status || "static-canon",
    })))}
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderAgentOpportunityScorecard() {
  const scorecard = state.agentOpportunity || {};
  const upstream_forward_radar_gate = scorecard.upstream_forward_radar_gate || {};
  const forward_radar_blocked = upstream_forward_radar_gate.promotion_allowed === false || upstream_forward_radar_gate.status === "blocked" || Number(upstream_forward_radar_gate.blockers?.length || 0) > 0;
  const opportunities = scorecard.opportunities || [];
  const noGoZones = scorecard.no_go_zones || [];
  fill(dom.agentOpportunityScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.frontstage_boundary || "frontstage work remains human-owned")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.opportunity_count || 0)}</strong><small>agents</small></span>
        <span><strong>${escapeHtml(scorecard.no_go_count || 0)}</strong><small>no-go</small></span>
        <span><strong>${escapeHtml(scorecard.total_reclaimable_hours_per_week || 0)}</strong><small>hrs/wk</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml((opportunities[0] && opportunities[0].agent_title) || scorecard.control_panel_label || "No backstage opportunities discovered")}</div>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Agent Opportunity upstream forward radar gate</strong>
        <span class="state-pill ${forward_radar_blocked ? "blocked" : "live-bound"}">${forward_radar_blocked ? "blocked" : "clear"}</span>
      </div>
      <small>${escapeHtml(upstream_forward_radar_gate.source || "upstream forward radar gate")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(upstream_forward_radar_gate.promotion_allowed === false ? "blocked" : "clear")}</strong><small>forward radar</small></span>
        <span><strong>${escapeHtml(upstream_forward_radar_gate.status || "unknown")}</strong><small>status</small></span>
        <span><strong>${escapeHtml(upstream_forward_radar_gate.radar_id || "none")}</strong><small>radar</small></span>
        <span><strong>${escapeHtml(upstream_forward_radar_gate.blockers?.length || 0)}</strong><small>blockers</small></span>
      </div>
    </article>
    ${scorecardLaneGrid(opportunities.slice(0, 6).map((item) => ({
      lane_id: item.activity_id,
      label: `${item.aaa_layer || "layer"} | ${item.agent_title || "agent"} | ${item.reclaimable_hours_per_week || 0} hrs/wk`,
      state: item.ready_for_agent_build === false ? "blocked" : item.aaa_layer === "autonomy" ? "shadow-only" : "live-bound",
    })))}
    <div class="token-grid">
      ${(scorecard.aaa_layers || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}
      ${noGoZones.slice(0, 4).map((item) => `<span class="token">human: ${escapeHtml(item.title || item.activity_id)}</span>`).join("")}
    </div>
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderHarnessProviderScorecard() {
  const scorecard = state.harnessProvider || {};
  const providers = scorecard.providers || [];
  fill(dom.harnessProviderScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.promotion_boundary || "external harnesses remain adapters")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.provider_count || 0)}</strong><small>providers</small></span>
        <span><strong>${escapeHtml(providers.filter((provider) => provider.lock_in_risk === "high").length)}</strong><small>high lock-in</small></span>
      </div>
    </article>
    ${scorecardLaneGrid(providers.slice(0, 6).map((provider) => ({
      lane_id: provider.provider_id,
      label: `${provider.tier} | ${provider.memory_portability} | ${provider.lock_in_risk} lock-in`,
      state: provider.lock_in_risk === "high" ? "degraded" : "live-bound",
    })))}
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderHarnessRoutingScorecard() {
  const scorecard = state.harnessRouting || {};
  const routes = scorecard.routing_profiles || [];
  fill(dom.harnessRoutingScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.routing_boundary || "model proxies remain governed adapters")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.route_count || 0)}</strong><small>routes</small></span>
        <span><strong>${escapeHtml(routes.filter((route) => route.privacy_posture === "external-proxy").length)}</strong><small>external</small></span>
        <span><strong>${escapeHtml((scorecard.security_rules || []).length)}</strong><small>rules</small></span>
      </div>
    </article>
    ${scorecardLaneGrid(routes.map((route) => ({
      lane_id: route.route_id,
      label: `${route.role || "role"} | ${route.privacy_posture || "privacy"} | ${route.cost_posture || "cost"}`,
      state: route.privacy_posture === "external-proxy" ? "shadow-only" : "live-bound",
    })))}
    <div class="token-grid">${(scorecard.security_rules || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderHarnessImprovementLedger() {
  const scorecard = state.harnessImprovementLedger || {};
  const latest = scorecard.latest_entry || {};
  const upstream_self_review_gate = latest.upstream_self_review_gate || {};
  const upstream_eval_gate = upstream_self_review_gate.upstream_eval_gate || {};
  const upstream_lifecycle_gate = upstream_eval_gate.upstream_lifecycle_gate || {};
  const self_review_blocked = upstream_self_review_gate.status === "blocked" || upstream_self_review_gate.review_state === "blocked-by-review" || upstream_eval_gate.promotion_allowed === false;
  const entries = scorecard.entries || [];
  fill(dom.harnessImprovementLedger, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.evolution_boundary || "harness evolution requires shadow runs and held-out eval separation")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.entry_count || 0)}</strong><small>entries</small></span>
        <span><strong>${escapeHtml(scorecard.shadow_validated_count || 0)}</strong><small>validated</small></span>
        <span><strong>${escapeHtml(scorecard.blocked_count || 0)}</strong><small>blocked</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(latest.entry_id || scorecard.control_panel_label || "No harness improvements recorded")}</div>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Harness upstream self-review gate</strong>
        <span class="state-pill ${self_review_blocked ? "blocked" : "live-bound"}">${self_review_blocked ? "blocked" : "clear"}</span>
      </div>
      <small>${escapeHtml(upstream_self_review_gate.source || "upstream self-review gate")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(upstream_self_review_gate.review_state || "unknown")}</strong><small>self-review</small></span>
        <span><strong>${escapeHtml(upstream_eval_gate.promotion_allowed === false ? "blocked" : "clear")}</strong><small>upstream eval</small></span>
        <span><strong>${escapeHtml(upstream_lifecycle_gate.lifecycle_status || "unknown")}</strong><small>lifecycle</small></span>
        <span><strong>${escapeHtml(upstream_self_review_gate.blockers?.length || 0)}</strong><small>blockers</small></span>
      </div>
    </article>
    ${scorecardLaneGrid(entries.slice(0, 6).map((entry) => ({
      lane_id: entry.entry_id,
      label: `${entry.change_type || "change"} | ${entry.score_delta || 0} delta | ${entry.harness_id || "harness"}`,
      state: entry.status || "static-canon",
    })))}
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderEdgeWorkloadRouterScorecard() {
  const scorecard = state.edgeWorkloadRouter || {};
  const latest = scorecard.latest_decision || {};
  const lanes = scorecard.lane_catalog || [];
  fill(dom.edgeWorkloadRouterScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.routing_rule || "hybrid local-first routing")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.decision_count || 0)}</strong><small>routes</small></span>
        <span><strong>${escapeHtml(latest.selected_lane_id || "standby")}</strong><small>selected</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(latest.explainability?.rule || scorecard.promotion_boundary || "Route decisions require hardware, privacy, latency, cost, and policy evidence")}</div>
    ${scorecardLaneGrid(lanes.map((lane) => ({
      lane_id: lane.lane_id,
      label: `${lane.label} | ${lane.privacy_posture} | ${lane.cost_posture}`,
      state: lane.lane_id === latest.selected_lane_id ? "live-bound" : "static-canon",
    })))}
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderMultimodalComputerUseScorecard() {
  const scorecard = state.multimodalComputerUse || {};
  const latest = scorecard.latest_plan || {};
  const plans = scorecard.plans || [];
  const route = latest.route_decision || {};
  fill(dom.multimodalComputerUseScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.execution_boundary || "observe-first-act-only-with-policy-human-confirmation")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.plan_count || 0)}</strong><small>plans</small></span>
        <span><strong>${escapeHtml(scorecard.shadow_count || 0)}</strong><small>shadow</small></span>
        <span><strong>${escapeHtml(scorecard.blocked_count || 0)}</strong><small>blocked</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(latest.user_goal || scorecard.promotion_boundary || "No computer-use plan recorded")}</div>
    <div class="token-grid">
      <span class="token">route: ${escapeHtml(route.selected_lane_id || "standby")}</span>
      <span class="token">sandbox: ${escapeHtml(latest.sandbox_mode || "shadow")}</span>
      <span class="token">permission: ${escapeHtml(latest.permission_scope || "none")}</span>
      <span class="token">local: ${escapeHtml(valueText(latest.local_only))}</span>
    </div>
    ${scorecardLaneGrid(plans.slice(0, 6).map((plan) => ({
      lane_id: plan.plan_id,
      label: `${(plan.requested_tasks || []).join(", ") || "observe"} | ${plan.sandbox_mode || "shadow"} | ${plan.permission_scope || "none"}`,
      state: plan.status || "static-canon",
    })))}
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderInferenceArchitectureScorecard() {
  const scorecard = state.inferenceArchitecture || {};
  const latest = scorecard.latest_plan || {};
  const plans = scorecard.plans || [];
  const strategy = latest.selected_strategy || {};
  const upstreamCacheGate = latest.upstream_cache_gate || {};
  const cacheBlocked = upstreamCacheGate.promotion_allowed === false || upstreamCacheGate.status === "blocked" || Number(upstreamCacheGate.blockers?.length || 0) > 0;
  fill(dom.inferenceArchitectureScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.architecture_boundary || "shadow benchmark before runtime architecture promotion")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.plan_count || 0)}</strong><small>plans</small></span>
        <span><strong>${escapeHtml(scorecard.shadow_count || 0)}</strong><small>shadow</small></span>
        <span><strong>${escapeHtml(scorecard.blocked_count || 0)}</strong><small>blocked</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Inference upstream cache gate</strong>
        <span class="state-pill ${cacheBlocked ? "blocked" : "live-bound"}">${cacheBlocked ? "blocked" : "clear"}</span>
      </div>
      <small>${escapeHtml(upstreamCacheGate.source || "effective context cache ledger")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(upstreamCacheGate.promotion_allowed === false ? "blocked" : "clear")}</strong><small>promotion</small></span>
        <span><strong>${escapeHtml(upstreamCacheGate.status || "not provided")}</strong><small>status</small></span>
        <span><strong>${escapeHtml(upstreamCacheGate.blockers?.length || 0)}</strong><small>blockers</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(latest.plan_id || "No inference architecture plans recorded")}</div>
    <div class="token-grid">
      ${["speculative_decoding", "prefix_cache", "continuous_batching", "disaggregated_prefill_decode"].map((key) => `
        <span class="token">${escapeHtml(pretty(key))}: ${escapeHtml(strategy[key] ? "on" : "off")}</span>
      `).join("")}
      <span class="token">KV: ${escapeHtml(strategy.kv_reuse || "standby")}</span>
    </div>
    ${scorecardLaneGrid(plans.slice(0, 6).map((plan) => ({
      lane_id: plan.plan_id,
      label: `${plan.workload_type || "workload"} | ${plan.selected_strategy?.runtime_mode || "runtime"} | ${plan.selected_strategy?.cache_scope || "cache"}`,
      state: plan.status || "static-canon",
    })))}
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderInferenceEconomyRouterScorecard() {
  const scorecard = state.inferenceEconomyRouter || {};
  const latest = scorecard.latest_decision || {};
  const decisions = scorecard.recent_decisions || [];
  const provider = latest.provider || {};
  const model = latest.model || {};
  const cost = latest.cost_ledger || {};
  fill(dom.inferenceEconomyRouterScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.routing_boundary || "privacy and safety policy route before cost")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.decision_count || 0)}</strong><small>routes</small></span>
        <span><strong>${escapeHtml(scorecard.routed_count || 0)}</strong><small>routed</small></span>
        <span><strong>${escapeHtml(scorecard.blocked_count || 0)}</strong><small>blocked</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(latest.decision_id || scorecard.control_panel_label || "No inference economy routes recorded")}</div>
    <div class="token-grid">
      <span class="token">tier: ${escapeHtml(latest.tier || "standby")}</span>
      <span class="token">provider: ${escapeHtml(provider.provider_id || "none")}</span>
      <span class="token">model: ${escapeHtml(model.model_id || "none")}</span>
      <span class="token">cost: ${escapeHtml(cost.estimated_cost_usd || 0)}</span>
      <span class="token">baseline: ${escapeHtml(cost.baseline_cost_usd || 0)}</span>
    </div>
    ${scorecardLaneGrid(decisions.slice(0, 6).map((decision) => ({
      lane_id: decision.decision_id,
      label: `${decision.tier || "tier"} | ${decision.provider?.provider_id || "provider"} | ${decision.specificity_category || "generic"}`,
      state: decision.status || "static-canon",
    })))}
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderCacheLedgerScorecard() {
  const scorecard = state.cacheLedger || {};
  const latest = scorecard.latest_entry || {};
  const entries = scorecard.entries || [];
  const context = latest.context_economics || {};
  const kv = latest.kv_cache || {};
  const upstreamQuantizationGate = latest.upstream_quantization_gate || {};
  const quantizationBlocked = upstreamQuantizationGate.promotion_allowed === false || upstreamQuantizationGate.status === "blocked" || Number(upstreamQuantizationGate.blockers?.length || 0) > 0;
  fill(dom.cacheLedgerScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.runtime_truth_boundary || "advertised context is not effective context without measurement")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.entry_count || 0)}</strong><small>entries</small></span>
        <span><strong>${escapeHtml(scorecard.average_effective_context_ratio || 0)}</strong><small>ctx ratio</small></span>
        <span><strong>${escapeHtml(scorecard.average_kv_cache_hit_rate || 0)}</strong><small>kv hit</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Cache upstream quantization gate</strong>
        <span class="state-pill ${quantizationBlocked ? "blocked" : "live-bound"}">${quantizationBlocked ? "blocked" : "clear"}</span>
      </div>
      <small>${escapeHtml(upstreamQuantizationGate.source || "quantization catalog")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(upstreamQuantizationGate.promotion_allowed === false ? "blocked" : "clear")}</strong><small>promotion</small></span>
        <span><strong>${escapeHtml(upstreamQuantizationGate.status || "not provided")}</strong><small>status</small></span>
        <span><strong>${escapeHtml(upstreamQuantizationGate.blockers?.length || 0)}</strong><small>blockers</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(latest.entry_id || scorecard.control_panel_label || "No effective context measurements recorded")}</div>
    <div class="token-grid">
      <span class="token">raw: ${escapeHtml(context.raw_context_tokens || 0)}</span>
      <span class="token">effective: ${escapeHtml(context.effective_context_tokens || 0)}</span>
      <span class="token">policy: ${escapeHtml(kv.policy || "standby")}</span>
      <span class="token">privacy: ${escapeHtml(latest.privacy?.privacy_scope || "session")}</span>
    </div>
    ${scorecardLaneGrid(entries.slice(0, 6).map((entry) => ({
      lane_id: entry.entry_id,
      label: `${entry.runtime_id || "runtime"} | ${entry.kv_cache?.policy || "kv"} | ${entry.context_economics?.effective_context_ratio || 0}`,
      state: entry.status || "static-canon",
    })))}
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderRuntimeWorkloadScorecards() {
  const scorecard = state.runtimeWorkloadScorecards || {};
  const latest = scorecard.latest_scorecard || {};
  const records = scorecard.scorecards || [];
  const latency = latest.latency || {};
  const throughput = latest.throughput || {};
  const cache = latest.cache || {};
  const upstreamProductizationGate = latest.upstream_productization_gate || {};
  const productizationBlocked = upstreamProductizationGate.release_ready === false || Number(upstreamProductizationGate.open_gates?.length || 0) > 0;
  fill(dom.runtimeWorkloadScorecards, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.runtime_truth_boundary || "runtime fit is measured per workload")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.scorecard_count || 0)}</strong><small>records</small></span>
        <span><strong>${escapeHtml(scorecard.average_ttft_ms_p95 || 0)}</strong><small>p95 TTFT</small></span>
        <span><strong>${escapeHtml(scorecard.average_decode_tokens_per_sec || 0)}</strong><small>tok/s</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Runtime upstream productization gate</strong>
        <span class="state-pill ${productizationBlocked ? "blocked" : "live-bound"}">${productizationBlocked ? "blocked" : "clear"}</span>
      </div>
      <small>${escapeHtml(upstreamProductizationGate.source || "productization readiness")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(upstreamProductizationGate.release_ready === false ? "blocked" : "clear")}</strong><small>release</small></span>
        <span><strong>${escapeHtml(upstreamProductizationGate.status || "not provided")}</strong><small>status</small></span>
        <span><strong>${escapeHtml(upstreamProductizationGate.open_gates?.length || 0)}</strong><small>open gates</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(latest.scorecard_id || scorecard.control_panel_label || "No workload scorecards recorded")}</div>
    <div class="token-grid">
      <span class="token">ttft p95: ${escapeHtml(latency.ttft_ms_p95 || 0)}</span>
      <span class="token">decode: ${escapeHtml(throughput.tokens_per_sec_decode || 0)}</span>
      <span class="token">kv hit: ${escapeHtml(cache.kv_cache_hit_rate || 0)}</span>
      <span class="token">hardware: ${escapeHtml(latest.hardware?.hardware_lane || "unknown")}</span>
    </div>
    ${scorecardLaneGrid(records.slice(0, 6).map((record) => ({
      lane_id: record.scorecard_id,
      label: `${record.backend || "backend"} | ${record.workload_type || "workload"} | ${record.hardware?.hardware_lane || "hardware"}`,
      state: record.status || "static-canon",
    })))}
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderBrowserContextScorecard() {
  const scorecard = state.browserContext || {};
  const latest = scorecard.latest_context || {};
  const contexts = scorecard.contexts || [];
  fill(dom.browserContextScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.privacy_boundary || "local browser context index")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.context_count || 0)}</strong><small>contexts</small></span>
        <span><strong>${escapeHtml(scorecard.indexed_count || 0)}</strong><small>indexed</small></span>
        <span><strong>${escapeHtml(scorecard.blocked_count || 0)}</strong><small>blocked</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(latest.title || scorecard.assimilation_pattern || "No local browser context indexed")}</div>
    ${scorecardLaneGrid(contexts.slice(0, 6).map((context) => ({
      lane_id: context.context_id,
      label: `${context.context_type || "context"} | ${context.source_permission || "unknown"} | ${context.local_only ? "local-only" : "review"}`,
      state: context.status || "static-canon",
    })))}
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderEngramMemoryScorecard() {
  const scorecard = state.engramMemory || {};
  const records = scorecard.recent_records || [];
  fill(dom.engramMemoryScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.memory_boundary || "explicit memory sidecar")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.record_count || 0)}</strong><small>records</small></span>
        <span><strong>${escapeHtml(scorecard.collision_slot_count || 0)}</strong><small>collisions</small></span>
        <span><strong>${escapeHtml(scorecard.head_count || 0)}</strong><small>heads</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml((records[0] && records[0].record_id) || scorecard.control_panel_label || "No Engram records stored")}</div>
    ${scorecardLaneGrid(records.slice(0, 6).map((record) => ({
      lane_id: record.record_id,
      label: `${record.sensitivity || "internal"} | ${(record.tags || []).join(", ") || "untagged"} | ${record.source_ref || "source"}`,
      state: record.sensitivity === "public" ? "live-bound" : "shadow-only",
    })))}
    <div class="token-grid">
      <span class="token">table: ${escapeHtml(scorecard.table_size || 0)}</span>
      <span class="token">orders: ${escapeHtml((scorecard.ngram_orders || []).join(", ") || "none")}</span>
    </div>
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderQuantizationCatalogScorecard() {
  const scorecard = state.quantizationCatalogScorecard || {};
  const latest = scorecard.latest_recommendation || {};
  const methods = scorecard.methods || [];
  const watchItems = scorecard.watch_items || [];
  const upstreamRuntimeGate = latest.upstream_runtime_scorecard_gate || {};
  const runtimeGateBlocked = upstreamRuntimeGate.promotion_allowed === false || upstreamRuntimeGate.status === "blocked" || Number(upstreamRuntimeGate.blockers?.length || 0) > 0;
  fill(dom.quantizationCatalogScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.catalog_boundary || "recommendation and shadow research only")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.method_count || 0)}</strong><small>methods</small></span>
        <span><strong>${escapeHtml(scorecard.kv_cache_candidate_count || 0)}</strong><small>KV lanes</small></span>
        <span><strong>${escapeHtml(scorecard.recommendation_count || 0)}</strong><small>recs</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Quantization upstream runtime gate</strong>
        <span class="state-pill ${runtimeGateBlocked ? "blocked" : "live-bound"}">${runtimeGateBlocked ? "blocked" : "clear"}</span>
      </div>
      <small>${escapeHtml(upstreamRuntimeGate.source || "runtime workload scorecards")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(upstreamRuntimeGate.promotion_allowed === false ? "blocked" : "clear")}</strong><small>promotion</small></span>
        <span><strong>${escapeHtml(upstreamRuntimeGate.status || "not provided")}</strong><small>status</small></span>
        <span><strong>${escapeHtml(upstreamRuntimeGate.blockers?.length || 0)}</strong><small>blockers</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(latest.selected_method?.label || "No quantization recommendation selected")}</div>
    ${scorecardLaneGrid(methods.slice(0, 7).map((method) => ({
      lane_id: method.method_id,
      label: `${method.format} | ${method.method_family} | ${method.status}`,
      state: method.status === "required-baseline" ? "live-bound" : "research-candidate",
    })))}
    <div class="token-grid">${watchItems.map((item) => `<span class="token">${escapeHtml(item)}</span>`).join("")}</div>
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderAdapterRegistryScorecard() {
  const scorecard = state.adapterRegistry || {};
  const latest = scorecard.latest_adapter || {};
  const adapters = scorecard.adapters || [];
  fill(dom.adapterRegistryScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.training_boundary || "registry only, no weight update")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.adapter_count || 0)}</strong><small>adapters</small></span>
        <span><strong>${escapeHtml(scorecard.shadow_count || 0)}</strong><small>shadow</small></span>
        <span><strong>${escapeHtml(scorecard.blocked_count || 0)}</strong><small>blocked</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(latest.adapter_id || scorecard.promotion_boundary || "No adapter candidates registered")}</div>
    ${scorecardLaneGrid(adapters.slice(0, 6).map((adapter) => ({
      lane_id: adapter.adapter_id,
      label: `${adapter.target_slot} | ${adapter.method?.type || "adapter"} | ${adapter.promotion_state}`,
      state: adapter.status || "static-canon",
    })))}
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderFineTuneDecisionGateScorecard() {
  const scorecard = state.fineTuneDecisionGate || {};
  const latest = scorecard.latest_decision || {};
  const decisions = scorecard.decisions || [];
  const datasetManifestStatus = latest.dataset_manifest_status || "unknown";
  const trainingReviewGate = latest.dataset_radar_training_review_gate || {};
  const trainingReviewBlockers = trainingReviewGate.blockers || [];
  const relevantFindings = (latest.decision_findings || []).filter((finding) => [
    "fine_tune_gate_requires_ready_dataset_manifest",
    "fine_tune_gate_dataset_radar_training_review_blocked",
  ].includes(finding.rule_id));
  fill(dom.fineTuneDecisionGateScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.training_boundary || "decision only, no training job")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.decision_count || 0)}</strong><small>decisions</small></span>
        <span><strong>${escapeHtml(scorecard.adapter_eligible_count || 0)}</strong><small>adapter eligible</small></span>
        <span><strong>${escapeHtml(scorecard.blocked_count || 0)}</strong><small>blocked</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(latest.decision_id || scorecard.assimilation_pattern || "No fine-tune decisions recorded")}</div>
    <div class="token-grid">
      <span class="token">path: ${escapeHtml(latest.recommended_path || "prompt-first")}</span>
      <span class="token">target: ${escapeHtml(pretty(latest.learning_target || "standby"))}</span>
      <span class="token">retrieval-first: ${escapeHtml(scorecard.retrieval_first_count || 0)}</span>
      <span class="token">adapter: ${escapeHtml(latest.adapter_training_allowed ? "eligible" : "blocked")}</span>
    </div>
    <div class="completion-scope">Fine-tune DatasetForge review gate: dataset_manifest_status ${escapeHtml(datasetManifestStatus)} | dataset_radar_training_review_gate ${trainingReviewGate.allowed === false ? "needs review" : "allowed or not attached"} | blocked ${(trainingReviewGate.blocked_source_ids || []).join(", ") || "none"}</div>
    ${scorecardLaneGrid(trainingReviewBlockers.slice(0, 6).map((blocker) => ({
      lane_id: blocker.source_id || blocker.review_packet_id || "training-review-blocker",
      label: `${blocker.review_state || "review"} | ${(blocker.blocking_fields || []).join(", ") || "no fields"} | ${blocker.reason || "review required"}`,
      state: "research-candidate",
    })))}
    ${scorecardLaneGrid(relevantFindings.slice(0, 6).map((finding) => ({
      lane_id: finding.rule_id || "fine-tune-finding",
      label: `${finding.severity || "blocking"} | ${finding.message || "Fine-tune gate finding"}`,
      state: finding.severity === "info" ? "static-canon" : "blocked",
    })))}
    ${scorecardLaneGrid(decisions.slice(0, 6).map((decision) => ({
      lane_id: decision.decision_id,
      label: `${decision.candidate_id || "candidate"} | ${decision.recommended_path || "path"} | ${decision.learning_target || "target"}`,
      state: decision.status || "static-canon",
    })))}
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderAdapterTrainingScorecard() {
  const scorecard = state.adapterTraining || {};
  const latest = scorecard.latest_plan || {};
  const plans = scorecard.plans || [];
  const hardware = latest.hardware_posture || {};
  const datasetManifestStatus = latest.dataset_manifest_status || "unknown";
  const trainingReviewGate = latest.dataset_radar_training_review_gate || {};
  const trainingReviewBlockers = trainingReviewGate.blockers || [];
  const relevantFindings = (latest.training_findings || []).filter((finding) => [
    "adapter_training_requires_ready_dataset_manifest",
    "adapter_training_dataset_radar_training_review_blocked",
    "adapter_training_requires_fine_tune_decision_allowance",
  ].includes(finding.rule_id));
  fill(dom.adapterTrainingScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.training_boundary || "plan only, no weight update")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.plan_count || 0)}</strong><small>plans</small></span>
        <span><strong>${escapeHtml(scorecard.shadow_count || 0)}</strong><small>shadow</small></span>
        <span><strong>${escapeHtml(scorecard.blocked_count || 0)}</strong><small>blocked</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(latest.plan_id || scorecard.assimilation_pattern || "No adapter training plan recorded")}</div>
    <div class="token-grid">
      <span class="token">method: ${escapeHtml(latest.method || "standby")}</span>
      <span class="token">hardware: ${escapeHtml(hardware.state || "unknown")}</span>
      <span class="token">examples: ${escapeHtml(latest.transformed_example_count || 0)}</span>
      <span class="token">GGUF: ${escapeHtml((latest.export_targets || []).includes("gguf") ? "planned" : "not requested")}</span>
    </div>
    <div class="completion-scope">Adapter training DatasetForge review gate: dataset_manifest_status ${escapeHtml(datasetManifestStatus)} | dataset_radar_training_review_gate ${trainingReviewGate.allowed === false ? "needs review" : "allowed or not attached"} | fine_tune_decision_allowance ${latest.fine_tune_adapter_training_allowed === false ? "blocked" : "allowed or not attached"} | blocked ${(trainingReviewGate.blocked_source_ids || []).join(", ") || "none"}</div>
    ${scorecardLaneGrid(trainingReviewBlockers.slice(0, 6).map((blocker) => ({
      lane_id: blocker.source_id || blocker.review_packet_id || "training-review-blocker",
      label: `${blocker.review_state || "review"} | ${(blocker.blocking_fields || []).join(", ") || "no fields"} | ${blocker.reason || "review required"}`,
      state: "research-candidate",
    })))}
    ${scorecardLaneGrid(relevantFindings.slice(0, 6).map((finding) => ({
      lane_id: finding.rule_id || "adapter-training-finding",
      label: `${finding.severity || "blocking"} | ${finding.message || "Adapter training gate finding"}`,
      state: finding.severity === "info" ? "static-canon" : "blocked",
    })))}
    ${scorecardLaneGrid(plans.slice(0, 6).map((plan) => ({
      lane_id: plan.plan_id,
      label: `${plan.adapter_id || "adapter"} | ${plan.method || "method"} | ${plan.hardware_posture?.state || "hardware"}`,
      state: plan.status || "static-canon",
    })))}
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderGrowthEngineScorecard() {
  const scorecard = state.growthEngine || {};
  const latest = scorecard.latest_cycle || {};
  const cycles = scorecard.cycles || [];
  const growthGate = latest.governance?.growth_gate || {};
  const growthBlockers = growthGate.blockers || [];
  const reviewerDecision = scorecard.latest_reviewer_decision || {};
  const hardGates = reviewerDecision.hard_gates || {};
  const latestTrainingRun = scorecard.latest_training_run || {};
  const trainingPrerequisites = latestTrainingRun.dataset_radar_training_prerequisites || {};
  const hiddenEvalAttestation = scorecard.latest_hidden_eval_attestation || {};
  const teacherCouncilManifest = scorecard.latest_teacher_council_manifest || {};
  const teacherCouncilEvidence = scorecard.latest_teacher_council_evidence || {};
  const latestDatasetManifest = scorecard.latest_dataset_manifest || {};
  const datasetSplits = latestDatasetManifest.splits || {};
  const teacherFreeHiddenSplit = datasetSplits.teacher_free_hidden || {};
  const datasetRadarLineage = latestDatasetManifest.dataset_radar_lineage || {};
  const datasetRadarSplitPolicy = datasetRadarLineage.split_policy || {};
  const latestStudentBirthRecord = scorecard.latest_student_birth_record || {};
  const latestModelGenome = scorecard.latest_model_genome || {};
  const modelGenomeArchitecture = latestModelGenome.architecture || {};
  const modelGenomeMoeRole = latestModelGenome.moe_role || {};
  const modelGenomeActivationPolicy = modelGenomeMoeRole.activation_policy || {};
  const latestTrainingLossTraceSummary = scorecard.latest_training_loss_trace_summary || {};
  const latestTrainingCheckpointSummary = scorecard.latest_training_checkpoint_summary || {};
  const latestTrainingOutputArtifacts = scorecard.latest_training_output_artifacts || {};
  const latestEvalScorecard = scorecard.latest_eval_scorecard || {};
  const latestEvalComparisonMatrix = scorecard.latest_eval_comparison_matrix || {};
  const latestEvalCaseResultsSummary = scorecard.latest_eval_case_results_summary || {};
  const latestCycleArtifactReplayKeys = scorecard.latest_cycle_artifact_replay_keys || [];
  const latestCycleArtifactReplayAvailability = scorecard.latest_cycle_artifact_replay_availability || {};
  const latestCycleArtifactReplayMissing = Object.keys(latestCycleArtifactReplayAvailability).filter(
    (key) => latestCycleArtifactReplayAvailability[key] === false
  );
  fill(dom.growthEngineScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.mutation_boundary || "dry-run-no-weight-update")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.cycle_count || 0)}</strong><small>cycles</small></span>
        <span><strong>${escapeHtml(scorecard.shadow_specialist_count || 0)}</strong><small>shadow</small></span>
        <span><strong>${escapeHtml(scorecard.promotable_count || 0)}</strong><small>promotable</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(latest.cycle_id || scorecard.teacher_ejection_boundary || "No growth cycles recorded")}</div>
    <div class="token-grid">
      <span class="token">mutation: ${escapeHtml(scorecard.mutation_boundary || "dry-run")}</span>
      <span class="token">ejection: ${escapeHtml(scorecard.teacher_ejection_boundary || "blocked")}</span>
      <span class="token">hidden eval: ${escapeHtml(scorecard.hidden_eval_boundary || "sealed")}</span>
      <span class="token">federation: ${escapeHtml(scorecard.federation_boundary || "sanitized only")}</span>
    </div>
    <div class="completion-scope">Growth Engine adapter-plan gate: ${escapeHtml(growthGate.gate_id || "growth_engine_adapter_training_gate")} | adapter_training_plan_ready ${growthGate.allowed === false ? "false" : "true or not attached"} | plan ${escapeHtml(growthGate.adapter_training_plan_ref || latest.state_refs?.adapter_training_plan_ref || "not attached")} | status ${escapeHtml(growthGate.adapter_training_plan_status || latest.state_refs?.adapter_training_plan_status || "unknown")}</div>
    <div class="completion-scope">Growth Engine hard gates: dataset_radar_source_review_passed ${hardGates.dataset_radar_source_review_passed ? "true" : "false"} | hidden_eval_attestation_passed ${hardGates.hidden_eval_attestation_passed ? "true" : "false"} | sealed_eval_not_teacher_visible ${hardGates.sealed_eval_not_teacher_visible ? "true" : "false"} | actual_weight_mutation_allowed ${hardGates.actual_weight_mutation_allowed ? "true" : "false"}</div>
    <div class="completion-scope">Growth Engine training prerequisites: actual_weight_mutation_blocked_until ${(trainingPrerequisites.actual_weight_mutation_blocked_until || []).join(", ") || "none"} | sealed_eval_source_ids ${(trainingPrerequisites.sealed_eval_source_ids || []).join(", ") || "none"} | sandbox_gpu_profile_ready ${(trainingPrerequisites.actual_weight_mutation_blocked_until || []).includes("sandbox_gpu_profile_ready") ? "required" : "not required"}</div>
    <div class="completion-scope">Growth Engine hidden eval attestation: teacher_visible ${hiddenEvalAttestation.teacher_visible ? "true" : "false"} | source_ids ${(hiddenEvalAttestation.source_ids || []).join(", ") || "none"} | split_policy_ref ${escapeHtml(hiddenEvalAttestation.split_policy_ref || "not recorded")}</div>
    <div class="completion-scope">Growth Engine teacher council replay: material_access_rule ${escapeHtml(teacherCouncilManifest.material_access_rule || "dataset-radar-only")} | dataset_radar_ref ${escapeHtml(teacherCouncilManifest.dataset_radar_ref || "not recorded")} | review_rule ${escapeHtml(teacherCouncilManifest.review_rule || "not recorded")}</div>
    <div class="completion-scope">Growth Engine teacher council evidence: teacher_output_count ${escapeHtml(teacherCouncilEvidence.teacher_output_count || 0)} | accepted_case_count ${escapeHtml(teacherCouncilEvidence.accepted_case_count || 0)} | validator_result_count ${escapeHtml(teacherCouncilEvidence.validator_result_count || 0)} | critique_count ${escapeHtml(teacherCouncilEvidence.critique_count || 0)} | rejected_variant_count ${escapeHtml(teacherCouncilEvidence.rejected_variant_count || 0)}</div>
    <div class="completion-scope">Growth Engine dataset split replay: train ${(datasetSplits.train || {}).case_count || 0} | validation ${(datasetSplits.validation || {}).case_count || 0} | heldout ${(datasetSplits.heldout || {}).case_count || 0} | teacher_free_hidden ${teacherFreeHiddenSplit.case_count || 0} | visible_to_training ${teacherFreeHiddenSplit.visible_to_training ? "true" : "false"} | visible_to_teacher_council ${teacherFreeHiddenSplit.visible_to_teacher_council ? "true" : "false"}</div>
    <div class="completion-scope">Growth Engine Dataset Radar lineage: source_ids ${(datasetRadarLineage.source_ids || []).join(", ") || "none"} | teacher_context_only_source_ids ${(datasetRadarSplitPolicy.teacher_context_only_source_ids || []).join(", ") || "none"} | sealed_eval_source_ids ${(datasetRadarSplitPolicy.sealed_eval_source_ids || []).join(", ") || "none"} | lineage_path ${escapeHtml(datasetRadarLineage.lineage_path || "not recorded")}</div>
    <div class="completion-scope">Growth Engine student birth replay: student_kind ${escapeHtml(latestStudentBirthRecord.student_kind || "not recorded")} | shadow_only ${latestStudentBirthRecord.shadow_only ? "true" : "false"} | temporary_until_reviewed ${latestStudentBirthRecord.temporary_until_reviewed ? "true" : "false"} | parent_node_refs ${(latestStudentBirthRecord.parent_node_refs || []).join(", ") || "none"}</div>
    <div class="completion-scope">Growth Engine model genome replay: model_family ${escapeHtml(latestModelGenome.model_family || "not recorded")} | adapter_type ${escapeHtml(modelGenomeArchitecture.adapter_type || "not recorded")} | activation_policy top_k ${escapeHtml(modelGenomeActivationPolicy.top_k || "not recorded")} shadow_only ${modelGenomeActivationPolicy.shadow_only ? "true" : "false"}</div>
    <div class="completion-scope">Growth Engine training loss trace replay: latest_training_loss_trace_summary step_count ${escapeHtml(latestTrainingLossTraceSummary.step_count || 0)} | first_loss ${escapeHtml(latestTrainingLossTraceSummary.first_loss ?? "not recorded")} | last_loss ${escapeHtml(latestTrainingLossTraceSummary.last_loss ?? "not recorded")} | final_step ${escapeHtml(latestTrainingLossTraceSummary.final_step ?? "not recorded")} | modes ${(latestTrainingLossTraceSummary.modes || []).join(", ") || "none"}</div>
    <div class="completion-scope">Growth Engine training checkpoint replay: latest_training_checkpoint_summary checkpoint_count ${escapeHtml(latestTrainingCheckpointSummary.checkpoint_count || 0)} | restore_validated_count ${escapeHtml(latestTrainingCheckpointSummary.restore_validated_count || 0)} | weight_snapshot_states ${(latestTrainingCheckpointSummary.weight_snapshot_states || []).join(", ") || "none"}</div>
    <div class="completion-scope">Growth Engine training output artifacts: artifact_count ${escapeHtml(latestTrainingOutputArtifacts.artifact_count || 0)} | artifact_refs ${(latestTrainingOutputArtifacts.artifact_refs || []).join(", ") || "none"} | kinds ${(latestTrainingOutputArtifacts.kinds || []).join(", ") || "none"}</div>
    <div class="completion-scope">Growth Engine eval scorecard replay: status ${escapeHtml(latestEvalScorecard.status || "not recorded")} | student_score ${escapeHtml(latestEvalScorecard.student_score ?? "not recorded")} | parent_score ${escapeHtml(latestEvalScorecard.parent_score ?? "not recorded")} | best_teacher_score ${escapeHtml(latestEvalScorecard.best_teacher_score ?? "not recorded")}</div>
    <div class="completion-scope">Growth Engine eval comparison replay: latest_eval_comparison_matrix student_vs_parent_margin ${escapeHtml(latestEvalComparisonMatrix.student_vs_parent_margin ?? "not recorded")} | student_vs_teacher_council_margin ${escapeHtml(latestEvalComparisonMatrix.student_vs_teacher_council_margin ?? "not recorded")}</div>
    <div class="completion-scope">Growth Engine eval case results replay: latest_eval_case_results_summary case_count ${escapeHtml(latestEvalCaseResultsSummary.case_count || 0)} | student_pass_count ${escapeHtml(latestEvalCaseResultsSummary.student_pass_count || 0)} | parent_pass_count ${escapeHtml(latestEvalCaseResultsSummary.parent_pass_count || 0)} | teacher_pass_count ${escapeHtml(latestEvalCaseResultsSummary.teacher_pass_count || 0)}</div>
    <div class="completion-scope">Growth Engine per-cycle replay endpoint: /ops/brain/growth-engine/cycles/${escapeHtml((latest.cycle_id || "").replace("cycle:", "") || "{cycle_id}")} | latest_cycle_artifact_replay_keys artifact_replay keys present ${latestCycleArtifactReplayKeys.join(", ") || "none"} | missing ${latestCycleArtifactReplayMissing.join(", ") || "none"}</div>
    <div class="completion-scope"><button type="button" data-growth-cycle-replay="${escapeAttr(latest.cycle_id || "")}" title="Fetch and render the full per-cycle artifact_replay">Inspect Per-Cycle Artifact Replay</button></div>
    ${renderGrowthCycleArtifactReplay()}
    ${scorecardLaneGrid(growthBlockers.slice(0, 6).map((blocker) => ({
      lane_id: blocker.rule_id || "growth-gate-blocker",
      label: `${blocker.severity || "hard_fail"} | ${blocker.message || blocker.reason || "growth gate blocker"}`,
      state: "blocked",
    })))}
    ${scorecardLaneGrid(cycles.slice(0, 6).map((cycle) => ({
      lane_id: cycle.cycle_id,
      label: `${cycle.target?.target_node_id || "target"} | ${cycle.birth_intent?.student_kind || "student"} | ${cycle.status || "state"}`,
      state: cycle.status || "static-canon",
    })))}
    <div class="token-grid">${(scorecard.required_artifacts || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderGrowthCycleArtifactReplay() {
  const replay = state.growthCycleReplay;
  if (!replay) {
    return "";
  }
  const artifactReplay = replay.artifact_replay || {};
  const cycleId = (replay.cycle_id || "").replace("cycle:", "");
  const rows = Object.keys(artifactReplay).map((key) => {
    const present = artifactReplay[key] !== null && artifactReplay[key] !== undefined;
    return `<div class="completion-scope">artifact_replay ${escapeHtml(key)}: ${present ? "present" : "absent"}</div>`;
  });
  return `
    <div class="runtime-scorecard-card">
      <div class="metric-head"><strong>Per-Cycle Artifact Replay</strong><span class="state-pill live-bound">${escapeHtml(cycleId || "cycle")}</span></div>
      ${rows.join("") || '<div class="completion-scope">No artifact_replay payload returned.</div>'}
    </div>`;
}

async function inspectLatestGrowthCycleReplay(event) {
  const button = event.target.closest("[data-growth-cycle-replay]");
  if (!button) {
    return;
  }
  const cycleId = (button.dataset.growthCycleReplay || "").replace("cycle:", "");
  if (!cycleId) {
    setConnection("error", "No growth cycle is available to replay.");
    return;
  }
  try {
    button.disabled = true;
    setConnection("", "Fetching per-cycle artifact replay...");
    const payload = await fetchJSON(`/ops/brain/growth-engine/cycles/${encodeURIComponent(cycleId)}`);
    state.growthCycleReplay = payload;
    renderGrowthEngineScorecard();
    setConnection("connected", `Loaded artifact_replay for ${payload.cycle_id || cycleId}`);
  } catch (error) {
    setConnection("error", error.message);
  } finally {
    button.disabled = false;
  }
}

function renderProductionSpineScorecard() {
  const scorecard = state.productionSpine || {};
  const latest = scorecard.latest_cycle || {};
  const latestLifecycle = scorecard.latest_lifecycle || {};
  const latest_lifecycle_replay_consistency = scorecard.latest_lifecycle_replay_consistency || {};
  const latest_lifecycle_artifact_bridge = scorecard.latest_lifecycle_artifact_bridge || {};
  const training_replay_evidence = scorecard.latest_lifecycle_training_replay_evidence || latestLifecycle.training_replay_evidence || {};
  const child_execution_replay_evidence = scorecard.latest_lifecycle_child_execution_replay_evidence || latestLifecycle.child_execution_replay_evidence || {};
  const hive_route_replay_evidence = scorecard.latest_lifecycle_hive_route_replay_evidence || latestLifecycle.hive_route_replay_evidence || {};
  const tensor_runtime_replay_evidence = scorecard.latest_lifecycle_tensor_runtime_replay_evidence || latestLifecycle.tensor_runtime_replay_evidence || {};
  const reviewer_confidence_evidence = scorecard.latest_lifecycle_reviewer_confidence_evidence || latestLifecycle.reviewer_confidence_evidence || {};
  const ejection_readiness_evidence = reviewer_confidence_evidence.ejection_readiness_evidence || latestLifecycle.sealed_eval?.ejection_readiness_evidence || {};
  const latest_reviewer_window_advancement = scorecard.latest_reviewer_window_advancement || {};
  const node_registry_replay_evidence = scorecard.latest_lifecycle_node_registry_replay_evidence || latestLifecycle.node_registry_replay_evidence || {};
  const node_registry_snapshot = scorecard.latest_lifecycle_node_registry_snapshot || latestLifecycle.node_registry_snapshot || {};
  const node_canary_guard_evidence = node_registry_replay_evidence.canary_promotion_guard_evidence || latestLifecycle.node_registry?.canary_promotion_guard_evidence || {};
  const node_reviewer_window_retirement_evidence = node_registry_replay_evidence.reviewer_window_retirement_evidence || latestLifecycle.node_registry?.reviewer_window_retirement_evidence || {};
  const federated_influence_replay_evidence = scorecard.latest_lifecycle_federated_influence_replay_evidence || latestLifecycle.federated_influence_replay_evidence || {};
  const recursive_dream_replay_evidence = scorecard.latest_lifecycle_recursive_dream_replay_evidence || latestLifecycle.recursive_dream_replay_evidence || {};
  const runtime_foundry_replay_evidence = scorecard.latest_lifecycle_runtime_foundry_replay_evidence || latestLifecycle.runtime_foundry_replay_evidence || {};
  const runtime_canary_guard_evidence = runtime_foundry_replay_evidence.runtime_canary_guard_evidence || runtime_foundry_replay_evidence.promotion_evidence?.runtime_canary_guard_evidence || latestLifecycle.runtime_foundry?.runtime_canary_guard_evidence || {};
  const productization_replay_evidence = scorecard.latest_lifecycle_productization_replay_evidence || latestLifecycle.productization_replay_evidence || {};
  const lifecycle_evidence_chain = scorecard.latest_lifecycle_evidence_chain || latestLifecycle.lifecycle_evidence_chain || {};
  const finish_readiness_map = scorecard.finish_readiness_map || {};
  const latest_real_training_gate = scorecard.latest_real_training_execution_gate || {};
  const real_training_artifact_trust_handoff = latest_real_training_gate.artifact_trust_handoff || {};
  const real_training_gate_request_template = scorecard.real_training_gate_request_template || {};
  const real_training_gate_request = real_training_gate_request_template.template || {};
  const reviewer_consistency = latestLifecycle.sealed_eval?.reviewer_consistency || {};
  const promotion_evidence = latestLifecycle.runtime_foundry?.promotion_evidence || {};
  const deep_replay = latestLifecycle.deep_replay || {};
  const deep_replay_drilldown_summary = scorecard.latest_deep_replay_drilldown_summary || {};
  const deep_replay_drilldowns = deep_replay_drilldown_summary.drilldowns || deep_replay.drilldowns || [];
  const deep_replay_bundle_request_template = scorecard.deep_replay_bundle_request_template || {};
  const deep_replay_request = deep_replay_bundle_request_template.template || {};
  const has_real_training_replay_drilldown = Boolean(
    deep_replay_drilldown_summary.has_real_training_artifact_trust || deep_replay_drilldowns.includes("real_training_artifact_trust")
  );
  const signature_policy = latestLifecycle.deep_replay?.signature_policy || {};
  const signature_summary = latestLifecycle.deep_replay?.signature_summary || {};
  const signer_readiness = latestLifecycle.signer_readiness || {};
  const project_local_signing_key_request_template = scorecard.project_local_signing_key_request_template || {};
  const project_local_signing_request = project_local_signing_key_request_template.template || {};
  const signed_deep_replay_handoff_request_template = scorecard.signed_deep_replay_handoff_request_template || {};
  const signed_replay_handoff_request = signed_deep_replay_handoff_request_template.template || {};
  const signed_replay_artifact_trust_rescan_request_template = scorecard.signed_replay_artifact_trust_rescan_request_template || {};
  const signed_replay_rescan_request = signed_replay_artifact_trust_rescan_request_template.template || {};
  const real_training_promotion_handoff_request_template = scorecard.real_training_promotion_handoff_request_template || {};
  const real_training_promotion_request = real_training_promotion_handoff_request_template.template || {};
  const runtime_node_activation_handoff_request_template = scorecard.runtime_node_activation_handoff_request_template || {};
  const runtime_node_activation_request = runtime_node_activation_handoff_request_template.template || {};
  const active_runtime_health_monitor_request_template = scorecard.active_runtime_health_monitor_request_template || {};
  const active_runtime_health_request = active_runtime_health_monitor_request_template.template || {};
  const teacher_ejection_parent_retirement_handoff_request_template = scorecard.teacher_ejection_parent_retirement_handoff_request_template || {};
  const teacher_ejection_retirement_request = teacher_ejection_parent_retirement_handoff_request_template.template || {};
  const production_support_bundle_export_request_template = scorecard.production_support_bundle_export_request_template || {};
  const production_support_bundle_request = production_support_bundle_export_request_template.template || {};
  const first_run_readiness_request_template = scorecard.first_run_readiness_request_template || {};
  const first_run_readiness_request = first_run_readiness_request_template.template || {};
  const crash_diagnostics_export_request_template = scorecard.crash_diagnostics_export_request_template || {};
  const crash_diagnostics_request = crash_diagnostics_export_request_template.template || {};
  const release_packaging_handoff_request_template = scorecard.release_packaging_handoff_request_template || {};
  const release_packaging_request = release_packaging_handoff_request_template.template || {};
  const release_go_no_go_review_request_template = scorecard.release_go_no_go_review_request_template || {};
  const release_go_no_go_request = release_go_no_go_review_request_template.template || {};
  const latest_manifest_preview_index = scorecard.latest_manifest_preview_index || {};
  const latest_manifest_preview_trust_summary = latest_manifest_preview_index.adapter_trust_summary || {};
  const manifest_preview_adapter_trust_status =
    release_go_no_go_request.adapter_artifact_trust_status ||
    release_packaging_request.adapter_artifact_trust_status ||
    production_support_bundle_request.adapter_artifact_trust_status ||
    "not_recorded";
  const manifest_preview_adapter_trust_clear = Boolean(
    release_go_no_go_request.adapter_artifact_trust_clear &&
    release_packaging_request.adapter_artifact_trust_clear &&
    production_support_bundle_request.adapter_artifact_trust_clear
  );
  const artifact_trust = latestLifecycle.artifact_trust || {};
  const adapter_artifact_scan = artifact_trust.adapter_artifact_scan || {};
  const artifact_trust_scan_request_template = scorecard.artifact_trust_scan_request_template || {};
  const artifact_trust_scan_request = artifact_trust_scan_request_template.template || {};
  const growth_engine_gate = latestLifecycle.growth_engine_gate || {};
  const productization = latest.productization || {};
  const productization_readiness_request_template = scorecard.productization_readiness_request_template || {};
  const productization_request_template = productization_readiness_request_template.template || {};
  const runtime_quantization_foundry_request_template = scorecard.runtime_quantization_foundry_request_template || {};
  const runtime_foundry_request_template = runtime_quantization_foundry_request_template.template || {};
  const sealed_eval_gauntlet_request_template = scorecard.sealed_eval_gauntlet_request_template || {};
  const sealed_eval_request = sealed_eval_gauntlet_request_template.template || {};
  const teacher_council_review_request_template = scorecard.teacher_council_review_request_template || {};
  const teacher_council_request = teacher_council_review_request_template.template || {};
  const training_backend_plan_request_template = scorecard.training_backend_plan_request_template || {};
  const training_backend_request = training_backend_plan_request_template.template || {};
  const sandbox_training_run_request_template = scorecard.sandbox_training_run_request_template || {};
  const sandbox_training_request = sandbox_training_run_request_template.template || {};
  const reviewer_window_request_template = scorecard.reviewer_window_request_template || {};
  const reviewer_window_request = reviewer_window_request_template.template || {};
  const node_registry_decision_request_template = scorecard.node_registry_decision_request_template || {};
  const node_registry_request = node_registry_decision_request_template.template || {};
  const federated_packet_request_template = scorecard.federated_packet_request_template || {};
  const federated_packet_request = federated_packet_request_template.template || {};
  const recursive_dream_cycle_request_template = scorecard.recursive_dream_cycle_request_template || {};
  const dream_cycle_request = recursive_dream_cycle_request_template.template || {};
  const tensor_program_request_template = scorecard.tensor_program_request_template || {};
  const tensor_program_request = tensor_program_request_template.template || {};
  const hive_moe_route_request_template = scorecard.hive_moe_route_request_template || {};
  const hive_route_request = hive_moe_route_request_template.template || {};
  const child_execution_request_template = scorecard.child_execution_request_template || {};
  const child_execution_request = child_execution_request_template.template || {};
  const upstream_agent_opportunity_gate = productization.upstream_agent_opportunity_gate || {};
  const agent_opportunity_blocked = upstream_agent_opportunity_gate.ready_for_agent_build === false || upstream_agent_opportunity_gate.opportunity_gate_state === "blocked-by-forward-radar" || Number(upstream_agent_opportunity_gate.blockers?.length || 0) > 0;
  const bridgePathCount = Object.values(latest_lifecycle_artifact_bridge).filter(Boolean).length;
  const operatorActionEntries = scorecard.operator_actions || {};
  const operatorActions = Object.entries(operatorActionEntries).map(([key, action]) => `
    <span class="token">${escapeHtml(pretty(key))} ${escapeHtml(action.method || "")} ${escapeHtml(action.endpoint || "")}</span>
  `).join("");
  fill(dom.productionSpineScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.mutation_boundary || "sandbox/eval/human gated")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.cycle_count || 0)}</strong><small>cycles</small></span>
        <span><strong>${escapeHtml(scorecard.lifecycle_count || 0)}</strong><small>lifecycles</small></span>
        <span><strong>${escapeHtml(scorecard.finish_surface_count || 0)}</strong><small>finish surfaces</small></span>
        <span><strong>${escapeHtml(productization.open_gates?.length || 0)}</strong><small>open gates</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(latest.cycle_id || scorecard.release_boundary || "No production-spine cycles recorded")}</div>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Finish readiness map</strong>
        <span class="state-pill ${finish_readiness_map.status === "ready" ? "live-bound" : "blocked"}">${escapeHtml(pretty(finish_readiness_map.status || "not recorded"))}</span>
      </div>
      <small>${escapeHtml(finish_readiness_map.mutation_boundary || "read-only finish gate map")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(finish_readiness_map.gate_count || 0)}</strong><small>finish gates</small></span>
        <span><strong>${escapeHtml(finish_readiness_map.ready_count || 0)}</strong><small>ready</small></span>
        <span><strong>${escapeHtml(finish_readiness_map.gated_count || 0)}</strong><small>gated</small></span>
        <span><strong>${escapeHtml(finish_readiness_map.blocked_count || 0)}</strong><small>blocked</small></span>
        <span><strong>${escapeHtml((finish_readiness_map.next_operator_actions || []).length)}</strong><small>next actions</small></span>
        <span><strong>${escapeHtml(finish_readiness_map.lifecycle_evidence_chain_ref || "none")}</strong><small>evidence chain</small></span>
      </div>
      <div class="token-grid">${(finish_readiness_map.gates || []).slice(0, 12).map((gate) => `<span class="token">${escapeHtml(pretty(gate.gate_id || "gate"))}: ${escapeHtml(pretty(gate.status || "unknown"))}</span>`).join("")}</div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Real training execution gate</strong>
        <span class="state-pill ${latest_real_training_gate.production_weight_mutation_allowed ? "live-bound" : "blocked"}">${escapeHtml(pretty(latest_real_training_gate.status || "not recorded"))}</span>
      </div>
      <small>${escapeHtml(latest_real_training_gate.mutation_boundary || "gate-only-no-training-executed")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(latest_real_training_gate.production_weight_mutation_allowed ? "yes" : "no")}</strong><small>weight mutation</small></span>
        <span><strong>${escapeHtml(latest_real_training_gate.execution_started ? "yes" : "no")}</strong><small>execution started</small></span>
        <span><strong>${escapeHtml((latest_real_training_gate.blocked_reasons || []).length)}</strong><small>blockers</small></span>
        <span><strong>${escapeHtml(latest_real_training_gate.license_state || "unknown")}</strong><small>license</small></span>
        <span><strong>${escapeHtml(latest_real_training_gate.hidden_eval_attestation?.leakage_scan_status || "unknown")}</strong><small>hidden eval</small></span>
        <span><strong>${escapeHtml(Object.keys(latest_real_training_gate.dependency_report || {}).length)}</strong><small>dependencies</small></span>
        <span><strong>${escapeHtml(real_training_artifact_trust_handoff.status || "blocked")}</strong><small>Real training artifact trust</small></span>
        <span><strong>${escapeHtml((real_training_artifact_trust_handoff.trusted_artifact_refs || []).length)}</strong><small>trusted refs</small></span>
        <span><strong>${escapeHtml((real_training_artifact_trust_handoff.blockers || []).length)}</strong><small>trust blockers</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Real training replay drilldowns</strong>
        <span class="state-pill ${has_real_training_replay_drilldown ? "live-bound" : "blocked"}">${has_real_training_replay_drilldown ? "real_training_artifact_trust" : "missing"}</span>
      </div>
      <small>${escapeHtml(deep_replay.replay_boundary || "signed replay drilldowns expose real-training artifact-trust handoff evidence")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(deep_replay_drilldown_summary.drilldown_count ?? deep_replay_drilldowns.length)}</strong><small>drilldowns</small></span>
        <span><strong>${escapeHtml(has_real_training_replay_drilldown ? "yes" : "no")}</strong><small>real_training_artifact_trust</small></span>
        <span><strong>${escapeHtml(deep_replay_drilldown_summary.artifact_count ?? deep_replay.artifact_count ?? 0)}</strong><small>replay artifacts</small></span>
        <span><strong>${escapeHtml(deep_replay_drilldown_summary.artifact_type_counts?.real_training_gate || 0)}</strong><small>real training gates</small></span>
        <span><strong>${escapeHtml(deep_replay.signature_policy?.current_signature_state || "unsigned_v0")}</strong><small>signature state</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Deep replay bundle request template</strong>
        <span class="state-pill ${deep_replay_bundle_request_template.ready_to_submit ? "live-bound" : "blocked"}">${deep_replay_bundle_request_template.ready_to_submit ? "ready" : "proofs missing"}</span>
      </div>
      <small>${escapeHtml(deep_replay_bundle_request_template.mutation_boundary || "template-only-deep-replay-build-no-production-mutation")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(deep_replay_request.replay_id || "none")}</strong><small>replay</small></span>
        <span><strong>${escapeHtml(deep_replay_request.current_signature_state || "unsigned_v0")}</strong><small>signature</small></span>
        <span><strong>${escapeHtml(deep_replay_request.next_signature_state || "signed_ed25519")}</strong><small>next signature</small></span>
        <span><strong>${escapeHtml(deep_replay_request.real_signing_blocker || "none")}</strong><small>signing blocker</small></span>
        <span><strong>${escapeHtml((deep_replay_request.drilldowns || []).length)}</strong><small>drilldowns</small></span>
        <span><strong>${escapeHtml((deep_replay_request.missing_drilldowns || []).length)}</strong><small>missing drilldowns</small></span>
        <span><strong>${escapeHtml(deep_replay_request.deep_replay_bundle_path ? "yes" : "no")}</strong><small>bundle path</small></span>
        <span><strong>${escapeHtml(deep_replay_request.artifact_index_path ? "yes" : "no")}</strong><small>artifact index</small></span>
        <span><strong>${escapeHtml(deep_replay_request.artifact_trust_scan?.quarantined_count ?? "none")}</strong><small>quarantined</small></span>
        <span><strong>${escapeHtml((deep_replay_bundle_request_template.missing_proof_fields || []).length)}</strong><small>missing proofs</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Real training gate request template</strong>
        <span class="state-pill ${real_training_gate_request_template.ready_to_submit ? "live-bound" : "blocked"}">${real_training_gate_request_template.ready_to_submit ? "ready" : "approval required"}</span>
      </div>
      <small>${escapeHtml(real_training_gate_request_template.mutation_boundary || "template-only-no-real-training-mutation")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(real_training_gate_request.cycle_id || "none")}</strong><small>cycle</small></span>
        <span><strong>${escapeHtml(real_training_gate_request.artifact_signing_ready ? "yes" : "no")}</strong><small>artifact signing</small></span>
        <span><strong>${escapeHtml(real_training_gate_request.artifact_trust_clear ? "yes" : "no")}</strong><small>artifact trust</small></span>
        <span><strong>${escapeHtml((real_training_gate_request.trusted_artifact_refs || []).length)}</strong><small>trusted refs</small></span>
        <span><strong>${escapeHtml((real_training_gate_request_template.manual_approval_fields || []).length)}</strong><small>manual approvals</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Lifecycle evidence chain</strong>
        <span class="state-pill ${lifecycle_evidence_chain.status === "ready" ? "live-bound" : "blocked"}">${escapeHtml(pretty(lifecycle_evidence_chain.status || "not recorded"))}</span>
      </div>
      <small>${escapeHtml(lifecycle_evidence_chain.mutation_boundary || "read-only lifecycle proof chain")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(lifecycle_evidence_chain.evidence_count || 0)}</strong><small>evidence blocks</small></span>
        <span><strong>${escapeHtml(lifecycle_evidence_chain.ready_count || 0)}</strong><small>ready</small></span>
        <span><strong>${escapeHtml(lifecycle_evidence_chain.blocked_count || 0)}</strong><small>gated</small></span>
        <span><strong>${escapeHtml(lifecycle_evidence_chain.artifact_ref_total || 0)}</strong><small>artifact refs</small></span>
        <span><strong>${escapeHtml(lifecycle_evidence_chain.operator_visible_count || 0)}</strong><small>operator visible</small></span>
        <span><strong>${escapeHtml((lifecycle_evidence_chain.blocked_evidence_ids || []).length)}</strong><small>blocked IDs</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Productization upstream agent opportunity gate</strong>
        <span class="state-pill ${agent_opportunity_blocked ? "blocked" : "live-bound"}">${agent_opportunity_blocked ? "blocked" : "clear"}</span>
      </div>
      <small>${escapeHtml(upstream_agent_opportunity_gate.source || "upstream agent opportunity gate")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(upstream_agent_opportunity_gate.ready_for_agent_build === false ? "blocked" : "clear")}</strong><small>agent build</small></span>
        <span><strong>${escapeHtml(upstream_agent_opportunity_gate.opportunity_gate_state || "unknown")}</strong><small>gate state</small></span>
        <span><strong>${escapeHtml(upstream_agent_opportunity_gate.blockers?.length || 0)}</strong><small>blockers</small></span>
        <span><strong>${escapeHtml(productization.release_ready ? "ready" : "blocked")}</strong><small>release</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Replay consistency</strong>
        <span class="state-pill ${latest_lifecycle_replay_consistency.passed ? "live-bound" : "blocked"}">${latest_lifecycle_replay_consistency.passed ? "passed" : "blocked"}</span>
      </div>
      <small>${escapeHtml(latestLifecycle.lifecycle_id || "No growth lifecycle replay recorded")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(latest_lifecycle_replay_consistency.integrity_state || "unknown")}</strong><small>integrity_state</small></span>
        <span><strong>${escapeHtml(latest_lifecycle_replay_consistency.integrity_blockers?.length || 0)}</strong><small>integrity blockers</small></span>
        <span><strong>${escapeHtml(latest_lifecycle_replay_consistency.checked_bridge_path_count || 0)}</strong><small>checked</small></span>
        <span><strong>${escapeHtml(latest_lifecycle_replay_consistency.indexed_bridge_path_count || 0)}</strong><small>indexed</small></span>
        <span><strong>${escapeHtml(bridgePathCount)}</strong><small>artifact bridge</small></span>
        <span><strong>${escapeHtml(latest_lifecycle_replay_consistency.expected_signature_state || "unsigned_v0")}</strong><small>signature</small></span>
        <span><strong>${escapeHtml(latest_lifecycle_replay_consistency.bridge_signature_state_mismatches?.length || 0)}</strong><small>signature mismatches</small></span>
        <span><strong>${escapeHtml(latest_lifecycle_replay_consistency.bridge_signature_verification_failures?.length || 0)}</strong><small>signature verification failures</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Sandbox training math replay</strong>
        <span class="state-pill ${training_replay_evidence.status === "ready" ? "live-bound" : "blocked"}">${escapeHtml(pretty(training_replay_evidence.status || "blocked"))}</span>
      </div>
      <small>${escapeHtml(training_replay_evidence.replay_boundary || "math and optimizer evidence required for training replay")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(training_replay_evidence.math_contract_present ? "yes" : "no")}</strong><small>math contract</small></span>
        <span><strong>${escapeHtml(training_replay_evidence.optimizer_state_present ? "yes" : "no")}</strong><small>optimizer state</small></span>
        <span><strong>${escapeHtml(training_replay_evidence.optimizer_state?.optimizer || "none")}</strong><small>optimizer</small></span>
        <span><strong>${escapeHtml(training_replay_evidence.optimizer_state?.steps || 0)}</strong><small>steps</small></span>
        <span><strong>${escapeHtml(training_replay_evidence.optimizer_state?.parameter_count || 0)}</strong><small>parameters</small></span>
        <span><strong>${escapeHtml(training_replay_evidence.math_contract?.loss || "none")}</strong><small>loss</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Training backend plan request template</strong>
        <span class="state-pill ${training_backend_plan_request_template.ready_to_submit ? "live-bound" : "blocked"}">${training_backend_plan_request_template.ready_to_submit ? "ready" : "proofs missing"}</span>
      </div>
      <small>${escapeHtml(training_backend_plan_request_template.mutation_boundary || "template-only-training-backend-plan-no-training-execution")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(training_backend_request.plan_id || "none")}</strong><small>plan</small></span>
        <span><strong>${escapeHtml(training_backend_request.method || "none")}</strong><small>method</small></span>
        <span><strong>${escapeHtml(training_backend_request.framework || "none")}</strong><small>framework</small></span>
        <span><strong>${escapeHtml(training_backend_request.support_state || "none")}</strong><small>support state</small></span>
        <span><strong>${escapeHtml(training_backend_request.dependency_report?.ready ? "ready" : "blocked")}</strong><small>dependencies</small></span>
        <span><strong>${escapeHtml(training_backend_request.missing_dependency_count || 0)}</strong><small>missing deps</small></span>
        <span><strong>${escapeHtml(training_backend_request.training_config_path ? "yes" : "no")}</strong><small>config</small></span>
        <span><strong>${escapeHtml(training_backend_request.training_invocation_path ? "yes" : "no")}</strong><small>invocation</small></span>
        <span><strong>${escapeHtml((training_backend_request.output_contract_targets || []).length)}</strong><small>output targets</small></span>
        <span><strong>${escapeHtml((training_backend_plan_request_template.missing_proof_fields || []).length)}</strong><small>missing proofs</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Sandbox training-run request template</strong>
        <span class="state-pill ${sandbox_training_run_request_template.ready_to_submit ? "live-bound" : "blocked"}">${sandbox_training_run_request_template.ready_to_submit ? "ready" : "proofs missing"}</span>
      </div>
      <small>${escapeHtml(sandbox_training_run_request_template.mutation_boundary || "template-only-sandbox-training-no-production-weight-mutation")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(sandbox_training_request.cycle_id || "none")}</strong><small>cycle</small></span>
        <span><strong>${escapeHtml(sandbox_training_request.training_backend_plan_ref || "none")}</strong><small>backend plan</small></span>
        <span><strong>${escapeHtml(sandbox_training_request.method || "none")}</strong><small>method</small></span>
        <span><strong>${escapeHtml(sandbox_training_request.framework || "none")}</strong><small>framework</small></span>
        <span><strong>${escapeHtml((sandbox_training_request.training_modes || []).length)}</strong><small>modes</small></span>
        <span><strong>${escapeHtml(sandbox_training_request.training_dataset_row_count || 0)}</strong><small>dataset rows</small></span>
        <span><strong>${escapeHtml(sandbox_training_request.optimizer_state?.steps || 0)}</strong><small>optimizer steps</small></span>
        <span><strong>${escapeHtml(sandbox_training_request.checkpoint_path ? "yes" : "no")}</strong><small>checkpoint</small></span>
        <span><strong>${escapeHtml(sandbox_training_request.adapter_bundle_path ? "yes" : "no")}</strong><small>adapter bundle</small></span>
        <span><strong>${escapeHtml((sandbox_training_request.export_targets || []).length)}</strong><small>exports</small></span>
        <span><strong>${escapeHtml((sandbox_training_run_request_template.missing_proof_fields || []).length)}</strong><small>missing proofs</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Child execution replay</strong>
        <span class="state-pill ${child_execution_replay_evidence.status === "ready" ? "live-bound" : "blocked"}">${escapeHtml(pretty(child_execution_replay_evidence.status || "blocked"))}</span>
      </div>
      <small>${escapeHtml(child_execution_replay_evidence.mutation_boundary || "shadow child execution only")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(child_execution_replay_evidence.callable_runtime_verified ? "yes" : "no")}</strong><small>callable runtime</small></span>
        <span><strong>${escapeHtml(child_execution_replay_evidence.weights_source || "none")}</strong><small>weights source</small></span>
        <span><strong>${escapeHtml(child_execution_replay_evidence.runtime_pathway?.used_neural_bus ? "yes" : "no")}</strong><small>NeuralBus</small></span>
        <span><strong>${escapeHtml(child_execution_replay_evidence.runtime_pathway?.used_hive_blackboard ? "yes" : "no")}</strong><small>HiveBlackboard</small></span>
        <span><strong>${escapeHtml(child_execution_replay_evidence.runtime_pathway?.used_eval_hook ? "yes" : "no")}</strong><small>eval hook</small></span>
        <span><strong>${escapeHtml(child_execution_replay_evidence.output_summary?.prediction ?? "none")}</strong><small>output</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Child execution request template</strong>
        <span class="state-pill ${child_execution_request_template.ready_to_submit ? "live-bound" : "blocked"}">${child_execution_request_template.ready_to_submit ? "ready" : "proofs missing"}</span>
      </div>
      <small>${escapeHtml(child_execution_request_template.mutation_boundary || "template-only-shadow-child-execution-no-production-output-or-node-registry-mutation")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(child_execution_request.cycle_id || "none")}</strong><small>cycle</small></span>
        <span><strong>${escapeHtml(child_execution_request.student_id || "none")}</strong><small>student</small></span>
        <span><strong>${escapeHtml(child_execution_request.preferred_weight_artifact || "checkpoint")}</strong><small>preferred artifact</small></span>
        <span><strong>${escapeHtml(child_execution_request.weights_path ? "yes" : "no")}</strong><small>weights ref</small></span>
        <span><strong>${escapeHtml(child_execution_request.adapter_bundle_path ? "yes" : "no")}</strong><small>adapter bundle</small></span>
        <span><strong>${escapeHtml(child_execution_request.input?.x ?? "none")}</strong><small>input x</small></span>
        <span><strong>${escapeHtml(child_execution_request.neural_bus_required ? "yes" : "no")}</strong><small>NeuralBus</small></span>
        <span><strong>${escapeHtml(child_execution_request.hive_blackboard_required ? "yes" : "no")}</strong><small>HiveBlackboard</small></span>
        <span><strong>${escapeHtml(child_execution_request.eval_hook_required ? "yes" : "no")}</strong><small>eval hook</small></span>
        <span><strong>${escapeHtml((child_execution_request_template.missing_proof_fields || []).length)}</strong><small>missing proofs</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Hive-MoE route replay</strong>
        <span class="state-pill ${hive_route_replay_evidence.status === "ready" ? "live-bound" : "blocked"}">${escapeHtml(pretty(hive_route_replay_evidence.status || "blocked"))}</span>
      </div>
      <small>${escapeHtml(hive_route_replay_evidence.mutation_boundary || "shadow route only")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(hive_route_replay_evidence.routing_mode || "none")}</strong><small>routing mode</small></span>
        <span><strong>${escapeHtml(hive_route_replay_evidence.top_k || 0)}</strong><small>top_k</small></span>
        <span><strong>${escapeHtml(hive_route_replay_evidence.selected_nodes?.length || 0)}</strong><small>selected</small></span>
        <span><strong>${escapeHtml(hive_route_replay_evidence.candidate_count || 0)}</strong><small>candidates</small></span>
        <span><strong>${escapeHtml(hive_route_replay_evidence.route_quality?.confidence ?? 0)}</strong><small>confidence</small></span>
        <span><strong>${escapeHtml(hive_route_replay_evidence.routing_weight_update?.promotion_required ? "yes" : "no")}</strong><small>promotion gate</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Hive-MoE route request template</strong>
        <span class="state-pill ${hive_moe_route_request_template.ready_to_submit ? "live-bound" : "blocked"}">${hive_moe_route_request_template.ready_to_submit ? "ready" : "proofs missing"}</span>
      </div>
      <small>${escapeHtml(hive_moe_route_request_template.mutation_boundary || "template-only-shadow-route-no-active-router-weight-mutation")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(hive_route_request.cycle_id || "none")}</strong><small>cycle</small></span>
        <span><strong>${escapeHtml(Object.keys(hive_route_request.task_features || {}).length)}</strong><small>features</small></span>
        <span><strong>${escapeHtml((hive_route_request.candidates || []).length)}</strong><small>candidates</small></span>
        <span><strong>${escapeHtml(hive_route_request.top_k || 0)}</strong><small>top_k</small></span>
        <span><strong>${escapeHtml((hive_moe_route_request_template.missing_proof_fields || []).length)}</strong><small>missing proofs</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Tensor runtime replay</strong>
        <span class="state-pill ${tensor_runtime_replay_evidence.status === "ready" ? "live-bound" : "blocked"}">${escapeHtml(pretty(tensor_runtime_replay_evidence.status || "blocked"))}</span>
      </div>
      <small>${escapeHtml(tensor_runtime_replay_evidence.mutation_boundary || "shadow tensor program only")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(tensor_runtime_replay_evidence.op_count || 0)}</strong><small>ops</small></span>
        <span><strong>${escapeHtml(Object.keys(tensor_runtime_replay_evidence.parameter_refs || {}).length)}</strong><small>parameter refs</small></span>
        <span><strong>${escapeHtml(tensor_runtime_replay_evidence.optimizer_state?.optimizer || "none")}</strong><small>optimizer</small></span>
        <span><strong>${escapeHtml(Object.keys(tensor_runtime_replay_evidence.optimizer_state?.updated_parameters || {}).length)}</strong><small>updated params</small></span>
        <span><strong>${escapeHtml(tensor_runtime_replay_evidence.checkpoint?.restore_validated ? "yes" : "no")}</strong><small>restore proof</small></span>
        <span><strong>${escapeHtml(tensor_runtime_replay_evidence.result_digest || "none")}</strong><small>result digest</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Tensor program request template</strong>
        <span class="state-pill ${tensor_program_request_template.ready_to_submit ? "live-bound" : "blocked"}">${tensor_program_request_template.ready_to_submit ? "ready" : "proofs missing"}</span>
      </div>
      <small>${escapeHtml(tensor_program_request_template.mutation_boundary || "template-only-shadow-tensor-program-no-production-parameter-mutation")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(tensor_program_request.cycle_id || "none")}</strong><small>cycle</small></span>
        <span><strong>${escapeHtml((tensor_program_request.ops || []).length)}</strong><small>ops</small></span>
        <span><strong>${escapeHtml(Object.keys(tensor_program_request.parameter_refs || {}).length)}</strong><small>parameter refs</small></span>
        <span><strong>${escapeHtml(tensor_program_request.optimizer_state?.optimizer || "none")}</strong><small>optimizer</small></span>
        <span><strong>${escapeHtml(tensor_program_request.checkpoint?.restore_validated ? "yes" : "no")}</strong><small>restore proof</small></span>
        <span><strong>${escapeHtml((tensor_program_request_template.missing_proof_fields || []).length)}</strong><small>missing proofs</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Growth Engine gate</strong>
        <span class="state-pill ${growth_engine_gate.allowed === false ? "blocked" : "live-bound"}">${growth_engine_gate.allowed === false ? "blocked" : "clear"}</span>
      </div>
      <small>${escapeHtml(growth_engine_gate.gate_id || "growth_engine_gate")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(growth_engine_gate.adapter_training_plan_status || "unknown")}</strong><small>adapter_training_plan_status</small></span>
        <span><strong>${escapeHtml(growth_engine_gate.adapter_training_plan_ref || "none")}</strong><small>adapter plan</small></span>
        <span><strong>${escapeHtml(growth_engine_gate.blockers?.length || 0)}</strong><small>blockers</small></span>
        <span><strong>${escapeHtml(growth_engine_gate.source || "not provided")}</strong><small>source</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Replay signature_policy</strong>
        <span class="state-pill ${signature_policy.production_promotion_requires_real_signing ? "blocked" : "live-bound"}">${signature_policy.production_promotion_requires_real_signing ? "real signing required" : "signing ready"}</span>
      </div>
      <small>${escapeHtml(signature_policy.real_signing_blocker || "real signing key management ready")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(signature_policy.current_signature_state || "unsigned_v0")}</strong><small>current</small></span>
        <span><strong>${escapeHtml(signature_policy.next_signature_state || "signed_ed25519")}</strong><small>next</small></span>
        <span><strong>${escapeHtml(signature_policy.unsigned_state_allowed_for?.length || 0)}</strong><small>allowed unsigned</small></span>
        <span><strong>${escapeHtml(signature_summary.signed_count || 0)}</strong><small>signed</small></span>
        <span><strong>${escapeHtml(signature_summary.unsigned_count || 0)}</strong><small>unsigned</small></span>
        <span><strong>${escapeHtml(signature_summary.signing_coverage ?? 0)}</strong><small>signing coverage</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Replay signer_readiness</strong>
        <span class="state-pill ${signer_readiness.status === "ready" ? "live-bound" : "blocked"}">${escapeHtml(pretty(signer_readiness.status || "blocked"))}</span>
      </div>
      <small>${escapeHtml(signer_readiness.production_mutation_blocker || "production signer ready")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(signer_readiness.current_signature_state || "unsigned_v0")}</strong><small>current</small></span>
        <span><strong>${escapeHtml(signer_readiness.next_signature_state || "signed_ed25519")}</strong><small>target</small></span>
        <span><strong>${escapeHtml(signer_readiness.signing_configuration_state || "missing")}</strong><small>signing_configuration_state</small></span>
        <span><strong>${escapeHtml(signer_readiness.signing_secret_persisted ? "yes" : "no")}</strong><small>secret persisted</small></span>
        <span><strong>${escapeHtml(signer_readiness.encrypted_key_file_persisted ? "yes" : "no")}</strong><small>encrypted key file</small></span>
        <span><strong>${escapeHtml(signer_readiness.durable_project_local_signer ? "yes" : "no")}</strong><small>durable signer</small></span>
        <span><strong>${escapeHtml(signer_readiness.signing_key_storage_scope || "none")}</strong><small>storage scope</small></span>
        <span><strong>${escapeHtml(signer_readiness.sandbox_shadow_replay_allowed ? "yes" : "no")}</strong><small>sandbox/shadow</small></span>
        <span><strong>${escapeHtml(signer_readiness.production_mutation_blocker ? "blocked" : "ready")}</strong><small>production signer</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Project-local signing key request template</strong>
        <span class="state-pill ${project_local_signing_key_request_template.ready_to_submit ? "live-bound" : "blocked"}">${project_local_signing_key_request_template.ready_to_submit ? "ready" : "passphrase required"}</span>
      </div>
      <small>${escapeHtml(project_local_signing_key_request_template.mutation_boundary || "template-only-project-local-encrypted-signing-key-no-secret-persistence")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(project_local_signing_request.key_id || "none")}</strong><small>key</small></span>
        <span><strong>${escapeHtml(project_local_signing_request.key_file_path ? "yes" : "no")}</strong><small>key file</small></span>
        <span><strong>${escapeHtml(project_local_signing_request.passphrase_required ? "yes" : "no")}</strong><small>passphrase required</small></span>
        <span><strong>${escapeHtml(project_local_signing_request.passphrase_persisted ? "yes" : "no")}</strong><small>passphrase persisted</small></span>
        <span><strong>${escapeHtml(project_local_signing_request.seed_generated_if_omitted ? "yes" : "no")}</strong><small>seed generated</small></span>
        <span><strong>${escapeHtml(project_local_signing_request.current_signer_status || "none")}</strong><small>signer status</small></span>
        <span><strong>${escapeHtml(project_local_signing_request.current_signature_state || "unsigned_v0")}</strong><small>current signature</small></span>
        <span><strong>${escapeHtml(project_local_signing_request.production_mutation_blocker || "none")}</strong><small>signing blocker</small></span>
        <span><strong>${escapeHtml((project_local_signing_key_request_template.manual_secret_fields || []).length)}</strong><small>manual secrets</small></span>
        <span><strong>${escapeHtml((project_local_signing_key_request_template.missing_proof_fields || []).length)}</strong><small>missing proofs</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Signed deep replay handoff request template</strong>
        <span class="state-pill ${signed_deep_replay_handoff_request_template.ready_to_submit ? "live-bound" : "blocked"}">${signed_deep_replay_handoff_request_template.ready_to_submit ? "ready" : "key/passphrase required"}</span>
      </div>
      <small>${escapeHtml(signed_deep_replay_handoff_request_template.mutation_boundary || "template-only-signed-replay-handoff-no-secret-persistence")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(signed_replay_handoff_request.replay_id || "none")}</strong><small>target replay</small></span>
        <span><strong>${escapeHtml(signed_replay_handoff_request.source_replay_id || "none")}</strong><small>source replay</small></span>
        <span><strong>${escapeHtml(signed_replay_handoff_request.signing_key_file ? "yes" : "no")}</strong><small>key file ref</small></span>
        <span><strong>${escapeHtml(signed_replay_handoff_request.signing_key_file_exists ? "yes" : "no")}</strong><small>key exists</small></span>
        <span><strong>${escapeHtml(signed_replay_handoff_request.signing_key_passphrase_provided ? "yes" : "no")}</strong><small>passphrase</small></span>
        <span><strong>${escapeHtml(signed_replay_handoff_request.current_signature_state || "unsigned_v0")}</strong><small>current signature</small></span>
        <span><strong>${escapeHtml(signed_replay_handoff_request.target_signature_state || "signed_ed25519")}</strong><small>target signature</small></span>
        <span><strong>${escapeHtml(signed_replay_handoff_request.artifact_trust_quarantined_count || 0)}</strong><small>quarantined</small></span>
        <span><strong>${escapeHtml((signed_deep_replay_handoff_request_template.manual_secret_fields || []).length)}</strong><small>manual secrets</small></span>
        <span><strong>${escapeHtml((signed_deep_replay_handoff_request_template.missing_proof_fields || []).length)}</strong><small>missing proofs</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Replay artifact_trust</strong>
        <span class="state-pill ${artifact_trust.quarantined_count ? "blocked" : "live-bound"}">${artifact_trust.quarantined_count ? "quarantined" : "trusted"}</span>
      </div>
      <small>${escapeHtml(artifact_trust.source || "deep_replay_bundle")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(artifact_trust.scan_count || 0)}</strong><small>scanned</small></span>
        <span><strong>${escapeHtml(artifact_trust.trusted_count || 0)}</strong><small>trusted replay artifacts</small></span>
        <span><strong>${escapeHtml(artifact_trust.quarantined_count || 0)}</strong><small>quarantined</small></span>
        <span><strong>${escapeHtml(adapter_artifact_scan.status || "not_recorded")}</strong><small>adapter artifact trust</small></span>
        <span><strong>${escapeHtml(adapter_artifact_scan.metadata?.relative_path ? "yes" : "no")}</strong><small>adapter relative path</small></span>
        <span><strong>${escapeHtml(adapter_artifact_scan.status === "quarantined" ? "yes" : "no")}</strong><small>adapter quarantine</small></span>
        <span><strong>${escapeHtml(artifact_trust.promotion_allowed ? "yes" : "no")}</strong><small>artifact trust promotion</small></span>
        <span><strong>${escapeHtml(artifact_trust.promotion_blockers?.length || 0)}</strong><small>promotion_blockers</small></span>
        <span><strong>${escapeHtml(artifact_trust.blocked_lifecycle_count || 0)}</strong><small>blocked lifecycles</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Artifact trust scan request template</strong>
        <span class="state-pill ${artifact_trust_scan_request_template.ready_to_submit ? "live-bound" : "blocked"}">${artifact_trust_scan_request_template.ready_to_submit ? "ready" : "proofs missing"}</span>
      </div>
      <small>${escapeHtml(artifact_trust_scan_request_template.mutation_boundary || "template-only-artifact-trust-scan-no-promotion")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(artifact_trust_scan_request.latest_scan_status || "none")}</strong><small>latest scan</small></span>
        <span><strong>${escapeHtml(artifact_trust_scan_request.artifact_type || "none")}</strong><small>artifact type</small></span>
        <span><strong>${escapeHtml(artifact_trust_scan_request.metadata?.signature_state || "unknown")}</strong><small>signature state</small></span>
        <span><strong>${escapeHtml(artifact_trust_scan_request.signature_required_for_trust ? "yes" : "no")}</strong><small>signature required</small></span>
        <span><strong>${escapeHtml((artifact_trust_scan_request.provenance_refs || []).length)}</strong><small>provenance refs</small></span>
        <span><strong>${escapeHtml(artifact_trust_scan_request.checksum ? "yes" : "no")}</strong><small>checksum</small></span>
        <span><strong>${escapeHtml(artifact_trust_scan_request.quarantined_count || 0)}</strong><small>quarantined</small></span>
        <span><strong>${escapeHtml((artifact_trust_scan_request_template.promotion_blockers || []).length)}</strong><small>promotion blockers</small></span>
        <span><strong>${escapeHtml((artifact_trust_scan_request.trust_findings || []).length)}</strong><small>trust findings</small></span>
        <span><strong>${escapeHtml((artifact_trust_scan_request_template.missing_proof_fields || []).length)}</strong><small>missing proofs</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Signed replay artifact-trust rescan request template</strong>
        <span class="state-pill ${signed_replay_artifact_trust_rescan_request_template.ready_to_submit ? "live-bound" : "blocked"}">${signed_replay_artifact_trust_rescan_request_template.ready_to_submit ? "ready" : "signed replay required"}</span>
      </div>
      <small>${escapeHtml(signed_replay_artifact_trust_rescan_request_template.mutation_boundary || "template-only-signed-replay-artifact-trust-rescan-no-promotion")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(signed_replay_rescan_request.target_replay_id || "none")}</strong><small>target replay</small></span>
        <span><strong>${escapeHtml(signed_replay_rescan_request.source_replay_id || "none")}</strong><small>source replay</small></span>
        <span><strong>${escapeHtml(signed_replay_rescan_request.current_artifact_trust_status || "none")}</strong><small>current trust</small></span>
        <span><strong>${escapeHtml(signed_replay_rescan_request.target_signature_state || "signed_ed25519")}</strong><small>target signature</small></span>
        <span><strong>${escapeHtml(signed_replay_rescan_request.signed_deep_replay_bundle_exists ? "yes" : "no")}</strong><small>signed bundle</small></span>
        <span><strong>${escapeHtml(signed_replay_rescan_request.signed_artifact_index_exists ? "yes" : "no")}</strong><small>signed index</small></span>
        <span><strong>${escapeHtml(signed_replay_rescan_request.source_quarantined_count || 0)}</strong><small>source quarantined</small></span>
        <span><strong>${escapeHtml(signed_replay_rescan_request.expected_adapter_artifact_trust_status_after_rescan || "not_recorded")}</strong><small>signed adapter trust</small></span>
        <span><strong>${escapeHtml(signed_replay_rescan_request.source_adapter_artifact_relative_path ? "yes" : "no")}</strong><small>signed adapter path</small></span>
        <span><strong>${escapeHtml(signed_replay_rescan_request.expected_quarantined_count_after_rescan ?? 0)}</strong><small>expected quarantined</small></span>
        <span><strong>${escapeHtml(signed_replay_rescan_request.expected_trusted_count_after_rescan || 0)}</strong><small>expected trusted</small></span>
        <span><strong>${escapeHtml((signed_replay_artifact_trust_rescan_request_template.missing_proof_fields || []).length)}</strong><small>missing proofs</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Reviewer consistency</strong>
        <span class="state-pill ${reviewer_consistency.teacher_ejection_eligible ? "live-bound" : "blocked"}">${reviewer_consistency.teacher_ejection_eligible ? "teacher ejection eligible" : "teacher ejection blocked"}</span>
      </div>
      <small>${escapeHtml(reviewer_consistency.teacher_ejection_blocker || "teacher ejection requires reviewer windows")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(reviewer_consistency.required_window_count || 0)}</strong><small>required</small></span>
        <span><strong>${escapeHtml(reviewer_consistency.passed_window_count || 0)}</strong><small>passed</small></span>
        <span><strong>${escapeHtml(reviewer_consistency.pending_window_count || 0)}</strong><small>pending</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Real-training promotion handoff request template</strong>
        <span class="state-pill ${real_training_promotion_handoff_request_template.ready_to_submit ? "live-bound" : "blocked"}">${real_training_promotion_handoff_request_template.ready_to_submit ? "ready" : "promotion gated"}</span>
      </div>
      <small>${escapeHtml(real_training_promotion_handoff_request_template.mutation_boundary || "template-only-real-training-promotion-handoff-production-mutation-default-off")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(real_training_promotion_request.target_signed_replay_id || "none")}</strong><small>signed replay</small></span>
        <span><strong>${escapeHtml(real_training_promotion_request.student_id || "none")}</strong><small>student</small></span>
        <span><strong>${escapeHtml(real_training_promotion_request.production_mutation_requested ? "yes" : "no")}</strong><small>mutation requested</small></span>
        <span><strong>${escapeHtml(real_training_promotion_request.operator_approved ? "yes" : "no")}</strong><small>operator</small></span>
        <span><strong>${escapeHtml(real_training_promotion_request.human_approved ? "yes" : "no")}</strong><small>human</small></span>
        <span><strong>${escapeHtml(real_training_promotion_request.allow_real_weight_mutation ? "yes" : "no")}</strong><small>weight mutation</small></span>
        <span><strong>${escapeHtml(real_training_promotion_request.signed_replay_trust_clear ? "yes" : "no")}</strong><small>signed trust</small></span>
        <span><strong>${escapeHtml(real_training_promotion_request.adapter_artifact_trust_status || "not_recorded")}</strong><small>adapter trust gate</small></span>
        <span><strong>${escapeHtml(real_training_promotion_request.adapter_artifact_trust_clear ? "yes" : "no")}</strong><small>adapter trust clear</small></span>
        <span><strong>${escapeHtml(real_training_promotion_request.sealed_eval_passed ? "yes" : "no")}</strong><small>sealed eval</small></span>
        <span><strong>${escapeHtml(real_training_promotion_request.reviewer_windows_ready ? "yes" : "no")}</strong><small>reviewer windows</small></span>
        <span><strong>${escapeHtml((real_training_promotion_handoff_request_template.promotion_blockers || []).length)}</strong><small>promotion blockers</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Reviewer confidence evidence</strong>
        <span class="state-pill ${reviewer_confidence_evidence.teacher_ejection_eligible ? "live-bound" : "blocked"}">${reviewer_confidence_evidence.teacher_ejection_eligible ? "teacher ejection eligible" : "teacher ejection blocked"}</span>
      </div>
      <small>${escapeHtml(reviewer_confidence_evidence.teacher_ejection_blocker || "teacher ejection requires confidence and reviewer windows")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(reviewer_confidence_evidence.parent_surpass_rate ?? 0)}</strong><small>parent surpass rate</small></span>
        <span><strong>${escapeHtml(reviewer_confidence_evidence.teacher_surpass_rate ?? 0)}</strong><small>teacher surpass rate</small></span>
        <span><strong>${escapeHtml(reviewer_confidence_evidence.lower_confidence_surpass_bound ?? 0)}</strong><small>lower bound</small></span>
        <span><strong>${escapeHtml(reviewer_confidence_evidence.passed_window_count || 0)}</strong><small>passed windows</small></span>
        <span><strong>${escapeHtml(reviewer_confidence_evidence.pending_window_count || 0)}</strong><small>pending windows</small></span>
        <span><strong>${escapeHtml(ejection_readiness_evidence.status || "gated")}</strong><small>Ejection readiness</small></span>
        <span><strong>${escapeHtml(ejection_readiness_evidence.teacher_ejection_allowed ? "yes" : "no")}</strong><small>ejection ready</small></span>
        <span><strong>${escapeHtml(ejection_readiness_evidence.pending_window_count || 0)}</strong><small>pending ejection windows</small></span>
        <span><strong>${escapeHtml(reviewer_confidence_evidence.hard_gates?.human_approved ? "yes" : "no")}</strong><small>human gate</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Runtime node activation handoff request template</strong>
        <span class="state-pill ${runtime_node_activation_handoff_request_template.ready_to_submit ? "live-bound" : "blocked"}">${runtime_node_activation_handoff_request_template.ready_to_submit ? "ready" : "activation gated"}</span>
      </div>
      <small>${escapeHtml(runtime_node_activation_handoff_request_template.mutation_boundary || "template-only-runtime-node-activation-no-live-roster-mutation")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(runtime_node_activation_request.student_id || "none")}</strong><small>student</small></span>
        <span><strong>${escapeHtml(runtime_node_activation_request.parent_node_ref || "none")}</strong><small>parent</small></span>
        <span><strong>${escapeHtml(runtime_node_activation_request.current_runtime_state || "shadow")}</strong><small>current state</small></span>
        <span><strong>${escapeHtml(runtime_node_activation_request.requested_runtime_state || "canary")}</strong><small>requested state</small></span>
        <span><strong>${escapeHtml(runtime_node_activation_request.rollback_restorable ? "yes" : "no")}</strong><small>rollback</small></span>
        <span><strong>${escapeHtml(runtime_node_activation_request.signed_replay_trust_clear ? "yes" : "no")}</strong><small>signed trust</small></span>
        <span><strong>${escapeHtml(runtime_node_activation_request.adapter_artifact_trust_status || "not_recorded")}</strong><small>runtime adapter trust</small></span>
        <span><strong>${escapeHtml(runtime_node_activation_request.adapter_artifact_trust_clear ? "yes" : "no")}</strong><small>runtime adapter clear</small></span>
        <span><strong>${escapeHtml(runtime_node_activation_request.reviewer_windows_ready ? "yes" : "no")}</strong><small>windows</small></span>
        <span><strong>${escapeHtml(runtime_node_activation_request.canary_window_passed ? "yes" : "no")}</strong><small>canary</small></span>
        <span><strong>${escapeHtml(runtime_node_activation_request.production_mutation_allowed ? "yes" : "no")}</strong><small>mutation</small></span>
        <span><strong>${escapeHtml((runtime_node_activation_handoff_request_template.activation_blockers || []).length)}</strong><small>activation blockers</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Reviewer window advancement</strong>
        <span class="state-pill ${latest_reviewer_window_advancement.status === "reviewer_window_recorded" ? "live-bound" : "blocked"}">${escapeHtml(pretty(latest_reviewer_window_advancement.status || "not recorded"))}</span>
      </div>
      <small>${escapeHtml(latest_reviewer_window_advancement.ejection_readiness_evidence?.mutation_boundary || "reviewer windows must be recorded before teacher ejection")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(latest_reviewer_window_advancement.window || "none")}</strong><small>window</small></span>
        <span><strong>${escapeHtml(latest_reviewer_window_advancement.window_status || "pending")}</strong><small>window status</small></span>
        <span><strong>${escapeHtml(latest_reviewer_window_advancement.ejection_readiness_evidence?.status || "gated")}</strong><small>ejection readiness</small></span>
        <span><strong>${escapeHtml(latest_reviewer_window_advancement.ejection_readiness_evidence?.pending_window_count || 0)}</strong><small>pending windows</small></span>
        <span><strong>${escapeHtml(scorecard.reviewer_window_advancement_count || 0)}</strong><small>recorded windows</small></span>
        <span><strong>${escapeHtml(operatorActionEntries.record_reviewer_window ? "available" : "missing")}</strong><small>record_reviewer_window</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Manifest preview index</strong>
        <span class="state-pill ${operatorActionEntries.inspect_manifest_previews ? "live-bound" : "blocked"}">${escapeHtml(operatorActionEntries.inspect_manifest_previews ? "endpoint ready" : "missing")}</span>
      </div>
      <small>manifest-preview replay index for support, release, first-run, crash, runtime-health, and teacher-ejection handoff manifests</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(operatorActionEntries.inspect_manifest_previews ? operatorActionEntries.inspect_manifest_previews.method : "GET")}</strong><small>method</small></span>
        <span><strong>${escapeHtml(operatorActionEntries.inspect_manifest_previews ? operatorActionEntries.inspect_manifest_previews.endpoint : "/ops/brain/production-spine/manifest-previews")}</strong><small>endpoint</small></span>
        <span><strong>${escapeHtml(manifest_preview_adapter_trust_status)}</strong><small>manifest adapter trust</small></span>
        <span><strong>${escapeHtml(manifest_preview_adapter_trust_clear ? "yes" : "no")}</strong><small>manifest adapter clear</small></span>
        <span><strong>${escapeHtml(latest_manifest_preview_trust_summary.trusted_count ?? 0)}</strong><small>manifest trusted count</small></span>
        <span><strong>${escapeHtml(latest_manifest_preview_trust_summary.quarantined_count ?? 0)}</strong><small>manifest quarantined count</small></span>
        <span><strong>${escapeHtml("read-only")}</strong><small>mutation boundary</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Teacher ejection / parent retirement handoff request template</strong>
        <span class="state-pill ${teacher_ejection_parent_retirement_handoff_request_template.ready_to_submit ? "live-bound" : "blocked"}">${teacher_ejection_parent_retirement_handoff_request_template.ready_to_submit ? "ready" : "retirement gated"}</span>
      </div>
      <small>${escapeHtml(teacher_ejection_parent_retirement_handoff_request_template.mutation_boundary || "template-only-teacher-ejection-parent-retirement-no-retirement-mutation")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(teacher_ejection_retirement_request.student_id || "none")}</strong><small>student</small></span>
        <span><strong>${escapeHtml(teacher_ejection_retirement_request.parent_node_ref || "none")}</strong><small>parent</small></span>
        <span><strong>${escapeHtml(teacher_ejection_retirement_request.teacher_ejection_allowed ? "yes" : "no")}</strong><small>teacher ejection</small></span>
        <span><strong>${escapeHtml(teacher_ejection_retirement_request.parent_retirement_allowed ? "yes" : "no")}</strong><small>parent retirement</small></span>
        <span><strong>${escapeHtml(teacher_ejection_retirement_request.post_promotion_window_passed ? "yes" : "no")}</strong><small>post promotion</small></span>
        <span><strong>${escapeHtml(teacher_ejection_retirement_request.ivy_grade_review_passed ? "yes" : "no")}</strong><small>Ivy review</small></span>
        <span><strong>${escapeHtml(teacher_ejection_retirement_request.greatly_outperforms_parent ? "yes" : "no")}</strong><small>parent surpass</small></span>
        <span><strong>${escapeHtml(teacher_ejection_retirement_request.child_retained_after_parent_retirement ? "yes" : "no")}</strong><small>child retained</small></span>
        <span><strong>${escapeHtml(teacher_ejection_retirement_request.rollback_retention_required ? "yes" : "no")}</strong><small>rollback retention</small></span>
        <span><strong>${escapeHtml(teacher_ejection_retirement_request.adapter_artifact_trust_status || "not_recorded")}</strong><small>ejection adapter trust</small></span>
        <span><strong>${escapeHtml(teacher_ejection_retirement_request.adapter_artifact_trust_clear ? "yes" : "no")}</strong><small>ejection adapter clear</small></span>
        <span><strong>${escapeHtml((teacher_ejection_parent_retirement_handoff_request_template.retirement_blockers || []).length)}</strong><small>retirement blockers</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Production support-bundle export request template</strong>
        <span class="state-pill ${production_support_bundle_export_request_template.ready_to_submit ? "live-bound" : "blocked"}">${production_support_bundle_export_request_template.ready_to_submit ? "ready" : "export gated"}</span>
      </div>
      <small>${escapeHtml(production_support_bundle_export_request_template.mutation_boundary || "template-only-support-bundle-export-no-secret-or-private-data-packaging")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(production_support_bundle_request.bundle_id || "none")}</strong><small>bundle</small></span>
        <span><strong>${escapeHtml(production_support_bundle_request.student_id || "none")}</strong><small>student</small></span>
        <span><strong>${escapeHtml(production_support_bundle_request.redact_secrets ? "yes" : "no")}</strong><small>redact secrets</small></span>
        <span><strong>${escapeHtml(production_support_bundle_request.include_raw_private_data ? "yes" : "no")}</strong><small>raw private</small></span>
        <span><strong>${escapeHtml(production_support_bundle_request.workspace_paths_redacted ? "yes" : "no")}</strong><small>path redaction</small></span>
        <span><strong>${escapeHtml(production_support_bundle_request.include_growth_cycle ? "yes" : "no")}</strong><small>growth</small></span>
        <span><strong>${escapeHtml(production_support_bundle_request.include_deep_replay ? "yes" : "no")}</strong><small>deep replay</small></span>
        <span><strong>${escapeHtml(production_support_bundle_request.include_artifact_trust ? "yes" : "no")}</strong><small>artifact trust</small></span>
        <span><strong>${escapeHtml(production_support_bundle_request.adapter_artifact_trust_status || "not_recorded")}</strong><small>support adapter trust</small></span>
        <span><strong>${escapeHtml(production_support_bundle_request.adapter_artifact_trust_clear ? "yes" : "no")}</strong><small>support adapter clear</small></span>
        <span><strong>${escapeHtml(production_support_bundle_request.include_kac_refs ? "yes" : "no")}</strong><small>KAC refs</small></span>
        <span><strong>${escapeHtml(production_support_bundle_request.include_runtime_health ? "yes" : "no")}</strong><small>runtime health</small></span>
        <span><strong>${escapeHtml((production_support_bundle_export_request_template.missing_proof_fields || []).length)}</strong><small>missing proofs</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>First-run readiness request template</strong>
        <span class="state-pill ${first_run_readiness_request_template.ready_to_submit ? "live-bound" : "blocked"}">${first_run_readiness_request_template.ready_to_submit ? "ready" : "first-run gated"}</span>
      </div>
      <small>${escapeHtml(first_run_readiness_request_template.mutation_boundary || "template-only-first-run-readiness-no-installer-or-cache-mutation")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(first_run_readiness_request.readiness_id || "none")}</strong><small>readiness</small></span>
        <span><strong>${escapeHtml(first_run_readiness_request.local_cache_controls_ready ? "yes" : "no")}</strong><small>cache controls</small></span>
        <span><strong>${escapeHtml(first_run_readiness_request.model_download_manager_ready ? "yes" : "no")}</strong><small>downloads</small></span>
        <span><strong>${escapeHtml(first_run_readiness_request.project_local_signing_key_ready ? "yes" : "no")}</strong><small>encrypted key</small></span>
        <span><strong>${escapeHtml(first_run_readiness_request.buyer_launcher_ready ? "yes" : "no")}</strong><small>launcher</small></span>
        <span><strong>${escapeHtml(first_run_readiness_request.support_bundle_ready ? "yes" : "no")}</strong><small>support bundle</small></span>
        <span><strong>${escapeHtml(first_run_readiness_request.crash_diagnostics_ready ? "yes" : "no")}</strong><small>diagnostics</small></span>
        <span><strong>${escapeHtml(first_run_readiness_request.adapter_artifact_trust_status || "not_recorded")}</strong><small>first-run adapter trust</small></span>
        <span><strong>${escapeHtml(first_run_readiness_request.adapter_artifact_trust_clear ? "yes" : "no")}</strong><small>first-run adapter clear</small></span>
        <span><strong>${escapeHtml(first_run_readiness_request.model_cache_root_path ? "set" : "missing")}</strong><small>model cache</small></span>
        <span><strong>${escapeHtml(first_run_readiness_request.download_cache_root_path ? "set" : "missing")}</strong><small>download cache</small></span>
        <span><strong>${escapeHtml((first_run_readiness_request_template.missing_proof_fields || []).length)}</strong><small>missing proofs</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Crash diagnostics export request template</strong>
        <span class="state-pill ${crash_diagnostics_export_request_template.ready_to_submit ? "live-bound" : "blocked"}">${crash_diagnostics_export_request_template.ready_to_submit ? "ready" : "diagnostics gated"}</span>
      </div>
      <small>${escapeHtml(crash_diagnostics_export_request_template.mutation_boundary || "template-only-crash-diagnostics-export-no-secret-or-private-data-packaging")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(crash_diagnostics_request.diagnostics_id || "none")}</strong><small>diagnostics</small></span>
        <span><strong>${escapeHtml(crash_diagnostics_request.crash_diagnostics_ready ? "yes" : "no")}</strong><small>diagnostics ready</small></span>
        <span><strong>${escapeHtml(crash_diagnostics_request.support_bundle_ready ? "yes" : "no")}</strong><small>support bundle</small></span>
        <span><strong>${escapeHtml(crash_diagnostics_request.secret_scan_passed ? "yes" : "no")}</strong><small>secret scan</small></span>
        <span><strong>${escapeHtml(crash_diagnostics_request.redact_secrets ? "yes" : "no")}</strong><small>redact secrets</small></span>
        <span><strong>${escapeHtml(crash_diagnostics_request.include_raw_private_data ? "yes" : "no")}</strong><small>raw private</small></span>
        <span><strong>${escapeHtml(crash_diagnostics_request.workspace_paths_redacted ? "yes" : "no")}</strong><small>path redaction</small></span>
        <span><strong>${escapeHtml(crash_diagnostics_request.include_runtime_health ? "yes" : "no")}</strong><small>runtime health</small></span>
        <span><strong>${escapeHtml(crash_diagnostics_request.include_deep_replay ? "yes" : "no")}</strong><small>deep replay</small></span>
        <span><strong>${escapeHtml(crash_diagnostics_request.include_artifact_trust ? "yes" : "no")}</strong><small>artifact trust</small></span>
        <span><strong>${escapeHtml(crash_diagnostics_request.adapter_artifact_trust_status || "not_recorded")}</strong><small>crash adapter trust</small></span>
        <span><strong>${escapeHtml(crash_diagnostics_request.adapter_artifact_trust_clear ? "yes" : "no")}</strong><small>crash adapter clear</small></span>
        <span><strong>${escapeHtml((crash_diagnostics_export_request_template.missing_proof_fields || []).length)}</strong><small>missing proofs</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Release packaging handoff request template</strong>
        <span class="state-pill ${release_packaging_handoff_request_template.ready_to_submit ? "live-bound" : "blocked"}">${release_packaging_handoff_request_template.ready_to_submit ? "ready" : "release gated"}</span>
      </div>
      <small>${escapeHtml(release_packaging_handoff_request_template.mutation_boundary || "template-only-release-packaging-no-installer-build-or-public-release-mutation")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(release_packaging_request.release_id || "none")}</strong><small>release</small></span>
        <span><strong>${escapeHtml(release_packaging_request.ci_packaging_ready ? "yes" : "no")}</strong><small>CI packaging</small></span>
        <span><strong>${escapeHtml(release_packaging_request.buyer_launcher_ready ? "yes" : "no")}</strong><small>launcher</small></span>
        <span><strong>${escapeHtml(release_packaging_request.support_bundle_ready ? "yes" : "no")}</strong><small>support bundle</small></span>
        <span><strong>${escapeHtml(release_packaging_request.crash_diagnostics_ready ? "yes" : "no")}</strong><small>diagnostics</small></span>
        <span><strong>${escapeHtml(release_packaging_request.first_run_readiness_ready ? "yes" : "no")}</strong><small>first run</small></span>
        <span><strong>${escapeHtml(release_packaging_request.buyer_safe_defaults ? "yes" : "no")}</strong><small>buyer safe</small></span>
        <span><strong>${escapeHtml(release_packaging_request.artifact_signing_ready ? "yes" : "no")}</strong><small>signing</small></span>
        <span><strong>${escapeHtml(release_packaging_request.artifact_trust_clear ? "yes" : "no")}</strong><small>artifact trust</small></span>
        <span><strong>${escapeHtml(release_packaging_request.adapter_artifact_trust_status || "not_recorded")}</strong><small>release adapter trust</small></span>
        <span><strong>${escapeHtml(release_packaging_request.adapter_artifact_trust_clear ? "yes" : "no")}</strong><small>release adapter clear</small></span>
        <span><strong>${escapeHtml((release_packaging_handoff_request_template.missing_proof_fields || []).length)}</strong><small>missing proofs</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Release go/no-go review request template</strong>
        <span class="state-pill ${release_go_no_go_review_request_template.ready_to_submit ? "live-bound" : "blocked"}">${release_go_no_go_review_request_template.ready_to_submit ? "ready" : "go/no-go gated"}</span>
      </div>
      <small>${escapeHtml(release_go_no_go_review_request_template.mutation_boundary || "template-only-release-go-no-go-no-buyer-release-mutation")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(release_go_no_go_request.review_id || "none")}</strong><small>review</small></span>
        <span><strong>${escapeHtml(release_go_no_go_request.release_packaging_ready ? "yes" : "no")}</strong><small>release package</small></span>
        <span><strong>${escapeHtml(release_go_no_go_request.first_run_readiness_ready ? "yes" : "no")}</strong><small>first run</small></span>
        <span><strong>${escapeHtml(release_go_no_go_request.crash_diagnostics_ready ? "yes" : "no")}</strong><small>diagnostics</small></span>
        <span><strong>${escapeHtml(release_go_no_go_request.support_bundle_ready ? "yes" : "no")}</strong><small>support bundle</small></span>
        <span><strong>${escapeHtml(release_go_no_go_request.artifact_trust_clear ? "yes" : "no")}</strong><small>artifact trust</small></span>
        <span><strong>${escapeHtml(release_go_no_go_request.adapter_artifact_trust_status || "not_recorded")}</strong><small>go/no-go adapter trust</small></span>
        <span><strong>${escapeHtml(release_go_no_go_request.adapter_artifact_trust_clear ? "yes" : "no")}</strong><small>go/no-go adapter clear</small></span>
        <span><strong>${escapeHtml(release_go_no_go_request.signed_replay_trust_clear ? "yes" : "no")}</strong><small>signed replay</small></span>
        <span><strong>${escapeHtml(release_go_no_go_request.reviewer_windows_ready ? "yes" : "no")}</strong><small>windows</small></span>
        <span><strong>${escapeHtml(release_go_no_go_request.human_approved ? "yes" : "no")}</strong><small>human approval</small></span>
        <span><strong>${escapeHtml(release_go_no_go_request.buyer_release_allowed ? "yes" : "no")}</strong><small>buyer release</small></span>
        <span><strong>${escapeHtml((release_go_no_go_review_request_template.release_blockers || []).length)}</strong><small>blockers</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Active runtime health monitor request template</strong>
        <span class="state-pill ${active_runtime_health_monitor_request_template.ready_to_submit ? "live-bound" : "blocked"}">${active_runtime_health_monitor_request_template.ready_to_submit ? "ready" : "monitor gated"}</span>
      </div>
      <small>${escapeHtml(active_runtime_health_monitor_request_template.mutation_boundary || "template-only-runtime-health-monitor-no-auto-disable-without-submitted-observations")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(active_runtime_health_request.student_id || "none")}</strong><small>student</small></span>
        <span><strong>${escapeHtml(active_runtime_health_request.current_runtime_state || "shadow")}</strong><small>runtime state</small></span>
        <span><strong>${escapeHtml(active_runtime_health_request.monitor_window || "canary_runtime")}</strong><small>window</small></span>
        <span><strong>${escapeHtml(active_runtime_health_request.rollback_snapshot_path ? "yes" : "no")}</strong><small>rollback</small></span>
        <span><strong>${escapeHtml(active_runtime_health_request.signed_replay_trust_clear ? "yes" : "no")}</strong><small>signed trust</small></span>
        <span><strong>${escapeHtml(active_runtime_health_request.adapter_artifact_trust_status || "not_recorded")}</strong><small>health adapter trust</small></span>
        <span><strong>${escapeHtml(active_runtime_health_request.adapter_artifact_trust_clear ? "yes" : "no")}</strong><small>health adapter clear</small></span>
        <span><strong>${escapeHtml(active_runtime_health_request.health_window_started ? "yes" : "no")}</strong><small>started</small></span>
        <span><strong>${escapeHtml(active_runtime_health_request.max_error_rate ?? 0.02)}</strong><small>max error</small></span>
        <span><strong>${escapeHtml(active_runtime_health_request.max_p95_latency_ms || 2000)}</strong><small>p95 ms</small></span>
        <span><strong>${escapeHtml(active_runtime_health_request.max_route_share ?? 0.1)}</strong><small>route share</small></span>
        <span><strong>${escapeHtml((active_runtime_health_monitor_request_template.health_blockers || []).length)}</strong><small>health blockers</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Sealed eval-gauntlet request template</strong>
        <span class="state-pill ${sealed_eval_gauntlet_request_template.ready_to_submit ? "live-bound" : "blocked"}">${sealed_eval_gauntlet_request_template.ready_to_submit ? "ready" : "sealed material required"}</span>
      </div>
      <small>${escapeHtml(sealed_eval_gauntlet_request_template.mutation_boundary || "template-only-sealed-eval-replay-raw-hidden-cases-not-exposed")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(sealed_eval_request.eval_id || "none")}</strong><small>eval</small></span>
        <span><strong>${escapeHtml(sealed_eval_request.student_id || "none")}</strong><small>student</small></span>
        <span><strong>${escapeHtml(sealed_eval_request.preferred_weight_artifact || "checkpoint")}</strong><small>sealed preferred artifact</small></span>
        <span><strong>${escapeHtml(sealed_eval_request.adapter_bundle_path ? "yes" : "no")}</strong><small>sealed adapter bundle</small></span>
        <span><strong>${escapeHtml(sealed_eval_request.hidden_eval_case_count || 0)}</strong><small>hidden cases</small></span>
        <span><strong>${escapeHtml((sealed_eval_request.hidden_eval_case_hashes || []).length)}</strong><small>case hashes</small></span>
        <span><strong>${escapeHtml(sealed_eval_request.student_parent_surpass_margin ?? 0)}</strong><small>parent margin</small></span>
        <span><strong>${escapeHtml(sealed_eval_request.student_teacher_surpass_margin ?? 0)}</strong><small>teacher margin</small></span>
        <span><strong>${escapeHtml(sealed_eval_request.lower_confidence_surpass_bound ?? 0)}</strong><small>confidence bound</small></span>
        <span><strong>${escapeHtml(sealed_eval_request.teacher_ejection_allowed ? "yes" : "no")}</strong><small>teacher ejection</small></span>
        <span><strong>${escapeHtml((sealed_eval_gauntlet_request_template.missing_proof_fields || []).length)}</strong><small>missing proofs</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Teacher council review request template</strong>
        <span class="state-pill ${teacher_council_review_request_template.ready_to_submit ? "live-bound" : "blocked"}">${teacher_council_review_request_template.ready_to_submit ? "ready" : "payload required"}</span>
      </div>
      <small>${escapeHtml(teacher_council_review_request_template.mutation_boundary || "template-only-teacher-council-review-raw-teacher-outputs-not-auto-resubmitted")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(teacher_council_request.review_id || "none")}</strong><small>review</small></span>
        <span><strong>${escapeHtml(teacher_council_request.teacher_count || 0)}</strong><small>teachers</small></span>
        <span><strong>${escapeHtml(teacher_council_request.license_gate_passed ? "yes" : "no")}</strong><small>license gate</small></span>
        <span><strong>${escapeHtml(teacher_council_request.accepted_teacher_ref || "none")}</strong><small>accepted teacher</small></span>
        <span><strong>${escapeHtml(teacher_council_request.disagreement_score ?? 0)}</strong><small>disagreement</small></span>
        <span><strong>${escapeHtml(teacher_council_request.validator_summary?.validator_count || 0)}</strong><small>validators</small></span>
        <span><strong>${escapeHtml(teacher_council_request.compiled_knowledge_context?.allowed === false ? "blocked" : "allowed")}</strong><small>KAC context</small></span>
        <span><strong>${escapeHtml((teacher_council_review_request_template.missing_proof_fields || []).length)}</strong><small>missing proofs</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Reviewer-window request template</strong>
        <span class="state-pill ${reviewer_window_request_template.ready_to_submit ? "live-bound" : "blocked"}">${reviewer_window_request_template.ready_to_submit ? "ready" : "proofs missing"}</span>
      </div>
      <small>${escapeHtml(reviewer_window_request_template.mutation_boundary || "template-only-no-teacher-ejection-or-parent-retirement")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(reviewer_window_request.cycle_id || "none")}</strong><small>cycle</small></span>
        <span><strong>${escapeHtml(reviewer_window_request.eval_id || "none")}</strong><small>eval</small></span>
        <span><strong>${escapeHtml(reviewer_window_request.window || "none")}</strong><small>next window</small></span>
        <span><strong>${escapeHtml((reviewer_window_request.passed_windows || []).length)}</strong><small>passed windows</small></span>
        <span><strong>${escapeHtml((reviewer_window_request_template.pending_windows || []).length)}</strong><small>pending windows</small></span>
        <span><strong>${escapeHtml((reviewer_window_request_template.missing_proof_fields || []).length)}</strong><small>missing proofs</small></span>
        <span><strong>${escapeHtml(reviewer_window_request.teacher_ejection_review_requested ? "yes" : "no")}</strong><small>teacher ejection review</small></span>
        <span><strong>${escapeHtml(reviewer_window_request.parent_retirement_review_requested ? "yes" : "no")}</strong><small>parent retirement review</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Node registry replay</strong>
        <span class="state-pill ${node_registry_replay_evidence.status === "ready" ? "live-bound" : "blocked"}">${escapeHtml(pretty(node_registry_replay_evidence.status || "blocked"))}</span>
      </div>
      <small>${escapeHtml(node_registry_replay_evidence.mutation_boundary || "node registry requires eval, approval, and rollback")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(node_registry_replay_evidence.student_state || "unknown")}</strong><small>student</small></span>
        <span><strong>${escapeHtml(node_registry_replay_evidence.parent_state || "unknown")}</strong><small>parent</small></span>
        <span><strong>${escapeHtml(node_registry_replay_evidence.parent_retirement_allowed ? "yes" : "no")}</strong><small>parent retirement</small></span>
        <span><strong>${escapeHtml(node_registry_replay_evidence.rollback_restorable ? "yes" : "no")}</strong><small>rollback</small></span>
        <span><strong>${escapeHtml(node_registry_replay_evidence.human_approved ? "yes" : "no")}</strong><small>human gate</small></span>
        <span><strong>${escapeHtml(node_reviewer_window_retirement_evidence.status || "not_required")}</strong><small>Reviewer-window retirement</small></span>
        <span><strong>${escapeHtml(node_reviewer_window_retirement_evidence.parent_retirement_allowed ? "yes" : "no")}</strong><small>reviewer retirement</small></span>
        <span><strong>${escapeHtml(node_canary_guard_evidence.active_deployment_allowed ? "yes" : "no")}</strong><small>active canary</small></span>
        <span><strong>${escapeHtml(node_canary_guard_evidence.canary_window_passed ? "yes" : "no")}</strong><small>canary window</small></span>
        <span><strong>${escapeHtml((node_registry_replay_evidence.blocked_reasons || []).length)}</strong><small>blockers</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Node registry decision request template</strong>
        <span class="state-pill ${node_registry_decision_request_template.ready_to_submit ? "live-bound" : "blocked"}">${node_registry_decision_request_template.ready_to_submit ? "ready" : "proofs missing"}</span>
      </div>
      <small>${escapeHtml(node_registry_decision_request_template.mutation_boundary || "template-only-no-node-registry-mutation")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(node_registry_request.cycle_id || "none")}</strong><small>cycle</small></span>
        <span><strong>${escapeHtml(node_registry_request.action || "none")}</strong><small>action</small></span>
        <span><strong>${escapeHtml(node_registry_request.student_id || "none")}</strong><small>student</small></span>
        <span><strong>${escapeHtml(node_registry_request.parent_node_ref || "none")}</strong><small>parent</small></span>
        <span><strong>${escapeHtml(node_registry_request.adapter_artifact_trust_status || "not_recorded")}</strong><small>node adapter trust</small></span>
        <span><strong>${escapeHtml(node_registry_request.adapter_artifact_trust_clear ? "yes" : "no")}</strong><small>node adapter clear</small></span>
        <span><strong>${escapeHtml((node_registry_decision_request_template.required_proof_fields || []).length)}</strong><small>proof fields</small></span>
        <span><strong>${escapeHtml((node_registry_decision_request_template.missing_proof_fields || []).length)}</strong><small>missing proofs</small></span>
        <span><strong>${escapeHtml(node_registry_request.human_approved ? "yes" : "no")}</strong><small>human gate</small></span>
        <span><strong>${escapeHtml(node_registry_request.shadow_runtime_window_passed ? "yes" : "no")}</strong><small>shadow canary</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Node registry snapshot</strong>
        <span class="state-pill ${node_registry_snapshot.status === "node_registry_snapshot_ready" ? "live-bound" : "blocked"}">${escapeHtml(pretty(node_registry_snapshot.status || "not recorded"))}</span>
      </div>
      <small>${escapeHtml(node_registry_snapshot.snapshot_id || "no snapshot recorded")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(node_registry_snapshot.adapter_artifact_trust_status || "not_recorded")}</strong><small>node registry snapshot trust</small></span>
        <span><strong>${escapeHtml(node_registry_snapshot.adapter_artifact_trust_clear ? "yes" : "no")}</strong><small>node registry snapshot clear</small></span>
        <span><strong>${escapeHtml(Object.keys(node_registry_snapshot.active_roster || {}).length)}</strong><small>active roster</small></span>
        <span><strong>${escapeHtml(node_registry_snapshot.rollback_restorable ? "yes" : "no")}</strong><small>snapshot rollback</small></span>
        <span><strong>${escapeHtml(node_registry_snapshot.events_count || 0)}</strong><small>registry events</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Federated influence replay</strong>
        <span class="state-pill ${federated_influence_replay_evidence.status === "ready" ? "live-bound" : "blocked"}">${escapeHtml(pretty(federated_influence_replay_evidence.status || "blocked"))}</span>
      </div>
      <small>${escapeHtml(federated_influence_replay_evidence.mutation_boundary || "sanitized federation only")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(federated_influence_replay_evidence.consent_granted ? "yes" : "no")}</strong><small>consent</small></span>
        <span><strong>${escapeHtml(federated_influence_replay_evidence.secure_aggregation_ready ? "yes" : "no")}</strong><small>secure agg</small></span>
        <span><strong>${escapeHtml(federated_influence_replay_evidence.differential_privacy?.enabled ? "yes" : "no")}</strong><small>DP</small></span>
        <span><strong>${escapeHtml(federated_influence_replay_evidence.poisoning_scan?.passed ? "yes" : "no")}</strong><small>poisoning</small></span>
        <span><strong>${escapeHtml(federated_influence_replay_evidence.trust_score ?? 0)}</strong><small>trust</small></span>
        <span><strong>${escapeHtml(federated_influence_replay_evidence.shadow_routing_influence?.active_route_mutation_allowed ? "yes" : "no")}</strong><small>active route</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Federated packet request template</strong>
        <span class="state-pill ${federated_packet_request_template.ready_to_submit ? "live-bound" : "blocked"}">${federated_packet_request_template.ready_to_submit ? "ready" : "proofs missing"}</span>
      </div>
      <small>${escapeHtml(federated_packet_request_template.mutation_boundary || "template-only-sanitized-federated-packet-no-active-route-mutation")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(federated_packet_request.cycle_id || "none")}</strong><small>cycle</small></span>
        <span><strong>${escapeHtml(federated_packet_request.source_node_ref || "none")}</strong><small>source node</small></span>
        <span><strong>${escapeHtml(federated_packet_request.consent_granted ? "yes" : "no")}</strong><small>consent</small></span>
        <span><strong>${escapeHtml(federated_packet_request.raw_content_included ? "yes" : "no")}</strong><small>raw content</small></span>
        <span><strong>${escapeHtml(Object.keys(federated_packet_request.local_metrics || {}).length)}</strong><small>metrics</small></span>
        <span><strong>${escapeHtml((federated_packet_request_template.missing_proof_fields || []).length)}</strong><small>missing proofs</small></span>
        <span><strong>${escapeHtml(federated_packet_request.active_route_mutation_allowed ? "yes" : "no")}</strong><small>active route</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Recursive dream replay</strong>
        <span class="state-pill ${recursive_dream_replay_evidence.status === "ready" ? "live-bound" : "blocked"}">${escapeHtml(pretty(recursive_dream_replay_evidence.status || "blocked"))}</span>
      </div>
      <small>${escapeHtml(recursive_dream_replay_evidence.mutation_boundary || "dream proposes only")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(recursive_dream_replay_evidence.candidate_count || 0)}</strong><small>candidates</small></span>
        <span><strong>${escapeHtml((recursive_dream_replay_evidence.candidate_types || []).length)}</strong><small>types</small></span>
        <span><strong>${escapeHtml((recursive_dream_replay_evidence.knowledge_artifact_refs || []).length)}</strong><small>KAC refs</small></span>
        <span><strong>${escapeHtml(recursive_dream_replay_evidence.compiled_knowledge_context_allowed ? "yes" : "no")}</strong><small>KAC gate</small></span>
        <span><strong>${escapeHtml(recursive_dream_replay_evidence.growth_seed?.sandbox_only ? "yes" : "no")}</strong><small>sandbox seed</small></span>
        <span><strong>${escapeHtml(recursive_dream_replay_evidence.production_mutation_allowed ? "yes" : "no")}</strong><small>production mutation</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Recursive dream-cycle request template</strong>
        <span class="state-pill ${recursive_dream_cycle_request_template.ready_to_submit ? "live-bound" : "blocked"}">${recursive_dream_cycle_request_template.ready_to_submit ? "ready" : "proofs missing"}</span>
      </div>
      <small>${escapeHtml(recursive_dream_cycle_request_template.mutation_boundary || "template-only-recursive-dream-proposes-sandbox-candidates")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(dream_cycle_request.cycle_id || "none")}</strong><small>cycle</small></span>
        <span><strong>${escapeHtml(dream_cycle_request.target_node_ref || "none")}</strong><small>target</small></span>
        <span><strong>${escapeHtml((dream_cycle_request.failure_refs || []).length)}</strong><small>failure refs</small></span>
        <span><strong>${escapeHtml(dream_cycle_request.federated_packet_signature ? "yes" : "no")}</strong><small>federated prior</small></span>
        <span><strong>${escapeHtml((dream_cycle_request.knowledge_artifact_refs || []).length)}</strong><small>KAC refs</small></span>
        <span><strong>${escapeHtml(dream_cycle_request.dream_temperature ?? "none")}</strong><small>dream temp</small></span>
        <span><strong>${escapeHtml((recursive_dream_cycle_request_template.missing_proof_fields || []).length)}</strong><small>missing proofs</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Runtime foundry</strong>
        <span class="state-pill ${promotion_evidence.promotion_allowed ? "live-bound" : "blocked"}">${escapeHtml(pretty(promotion_evidence.promotion_blocker || "promotion ready"))}</span>
      </div>
      <small>${escapeHtml(`${promotion_evidence.best_method || "no method"} | ${promotion_evidence.best_backend || "no backend"} | ${promotion_evidence.kv_cache || "no kv cache"}`)}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(promotion_evidence.quality_delta ?? 0)}</strong><small>quality delta</small></span>
        <span><strong>${escapeHtml(promotion_evidence.tokens_per_second ?? 0)}</strong><small>tok/s</small></span>
        <span><strong>${escapeHtml(promotion_evidence.memory_gb ?? 0)}</strong><small>GB</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Runtime foundry replay</strong>
        <span class="state-pill ${runtime_foundry_replay_evidence.promotion_allowed ? "live-bound" : "blocked"}">${escapeHtml(pretty(runtime_foundry_replay_evidence.promotion_blocker || runtime_foundry_replay_evidence.status || "blocked"))}</span>
      </div>
      <small>${escapeHtml(runtime_foundry_replay_evidence.mutation_boundary || "runtime method promotion requires proof")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(runtime_foundry_replay_evidence.backend_run_verified ? "yes" : "no")}</strong><small>backend proof</small></span>
        <span><strong>${escapeHtml(runtime_foundry_replay_evidence.benchmark_count || 0)}</strong><small>benchmarks</small></span>
        <span><strong>${escapeHtml((runtime_foundry_replay_evidence.candidate_backends || []).length)}</strong><small>backends</small></span>
        <span><strong>${escapeHtml((runtime_foundry_replay_evidence.kv_cache_methods_tested || []).length)}</strong><small>KV-cache</small></span>
        <span><strong>${escapeHtml(runtime_foundry_replay_evidence.best_candidate?.method || "none")}</strong><small>best method</small></span>
        <span><strong>${escapeHtml(runtime_foundry_replay_evidence.promotion_evidence?.quality_delta ?? 0)}</strong><small>quality delta</small></span>
        <span><strong>${escapeHtml(runtime_canary_guard_evidence.active_runtime_method_allowed ? "yes" : "no")}</strong><small>runtime canary</small></span>
        <span><strong>${escapeHtml(runtime_canary_guard_evidence.hidden_eval_delta_review_passed ? "yes" : "no")}</strong><small>eval delta</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Runtime quantization foundry request template</strong>
        <span class="state-pill ${runtime_quantization_foundry_request_template.ready_to_submit ? "live-bound" : "blocked"}">${runtime_quantization_foundry_request_template.ready_to_submit ? "ready" : "proofs missing"}</span>
      </div>
      <small>${escapeHtml(runtime_quantization_foundry_request_template.mutation_boundary || "template-only-no-runtime-method-mutation")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(runtime_foundry_request_template.cycle_id || "none")}</strong><small>cycle</small></span>
        <span><strong>${escapeHtml(runtime_foundry_request_template.model_ref || "none")}</strong><small>model</small></span>
        <span><strong>${escapeHtml((runtime_quantization_foundry_request_template.required_proof_fields || []).length)}</strong><small>proof fields</small></span>
        <span><strong>${escapeHtml((runtime_quantization_foundry_request_template.missing_proof_fields || []).length)}</strong><small>missing proofs</small></span>
        <span><strong>${escapeHtml((runtime_foundry_request_template.candidates || []).length)}</strong><small>candidates</small></span>
        <span><strong>${escapeHtml(runtime_foundry_request_template.backend_run_verified ? "yes" : "no")}</strong><small>backend proof</small></span>
        <span><strong>${escapeHtml(runtime_foundry_request_template.runtime_shadow_window_passed ? "yes" : "no")}</strong><small>shadow window</small></span>
        <span><strong>${escapeHtml(runtime_foundry_request_template.hidden_eval_delta_review_passed ? "yes" : "no")}</strong><small>hidden eval delta</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Productization replay</strong>
        <span class="state-pill ${productization_replay_evidence.release_ready ? "live-bound" : "blocked"}">${productization_replay_evidence.release_ready ? "release ready" : "release blocked"}</span>
      </div>
      <small>${escapeHtml(productization_replay_evidence.shareable_artifact_boundary || productization_replay_evidence.mutation_boundary || "release bundle only")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml((productization_replay_evidence.open_gates || []).length)}</strong><small>open gates</small></span>
        <span><strong>${escapeHtml(productization_replay_evidence.secret_scan_passed ? "yes" : "no")}</strong><small>secret scan</small></span>
        <span><strong>${escapeHtml(productization_replay_evidence.model_download_manager ? "yes" : "no")}</strong><small>downloads</small></span>
        <span><strong>${escapeHtml(productization_replay_evidence.support_bundle ? "yes" : "no")}</strong><small>support bundle</small></span>
        <span><strong>${escapeHtml(productization_replay_evidence.ci_packaging ? "yes" : "no")}</strong><small>CI packaging</small></span>
        <span><strong>${escapeHtml(productization_replay_evidence.buyer_safe_defaults ? "yes" : "no")}</strong><small>buyer-safe</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Productization readiness request template</strong>
        <span class="state-pill ${productization_readiness_request_template.ready_to_submit ? "live-bound" : "blocked"}">${productization_readiness_request_template.ready_to_submit ? "ready" : "proofs missing"}</span>
      </div>
      <small>${escapeHtml(productization_readiness_request_template.mutation_boundary || "template-only-no-release-mutation")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(productization_request_template.cycle_id || "none")}</strong><small>cycle</small></span>
        <span><strong>${escapeHtml((productization_readiness_request_template.required_proof_fields || []).length)}</strong><small>proof fields</small></span>
        <span><strong>${escapeHtml((productization_readiness_request_template.missing_proof_fields || []).length)}</strong><small>missing proofs</small></span>
        <span><strong>${escapeHtml(productization_request_template.secret_scan_passed ? "yes" : "no")}</strong><small>secret scan</small></span>
        <span><strong>${escapeHtml(productization_request_template.support_bundle ? "yes" : "no")}</strong><small>support bundle</small></span>
        <span><strong>${escapeHtml(productization_request_template.ci_packaging ? "yes" : "no")}</strong><small>CI packaging</small></span>
        <span><strong>${escapeHtml(productization_request_template.adapter_artifact_trust_status || "not_recorded")}</strong><small>productization adapter trust</small></span>
        <span><strong>${escapeHtml(productization_request_template.adapter_artifact_trust_clear ? "yes" : "no")}</strong><small>productization adapter clear</small></span>
      </div>
    </article>
    <div class="token-grid">${(scorecard.finish_surfaces || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
    ${scorecardLaneGrid((scorecard.cycles || []).slice(0, 6).map((cycle) => ({
      lane_id: cycle.cycle_id,
      label: `${cycle.productization?.release_ready ? "release ready" : "release gated"} | ${cycle.real_training_runner?.support_state || "training"} | ${cycle.sealed_eval_gauntlet?.promotion_allowed ? "promotable" : "shadow"}`,
      state: cycle.productization?.release_ready ? "live-bound" : "shadow-only",
    })))}
    <div class="completion-scope">Live production-spine action endpoints</div>
    <div class="token-grid">${operatorActions}</div>
    <div class="token-grid">${(productization.open_gates || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderDatasetForgeScorecard() {
  const scorecard = state.datasetForge || {};
  const latest = scorecard.latest_manifest || {};
  const manifests = scorecard.manifests || [];
  const latestBuild = state.datasetForgeManifest || {};
  const latestHandoff = latestDatasetForgeHandoff();
  const reviewPackets = latest.dataset_radar_review_packets || latestBuild.dataset_radar_review_packets || [];
  const trainingReviewGate = latest.dataset_radar_training_review_gate || latestBuild.dataset_radar_training_review_gate || {};
  const lineageSplitPolicy = latest.dataset_radar_lineage_split_policy || latestBuild.dataset_radar_lineage_split_policy || {};
  const datasetFlowLineage = state.controlPanel?.dataset_flow_view?.dataset_forge_lineage || {};
  const reviewBlockedLineage = datasetFlowLineage.review_blocked_lineage || [];
  fill(dom.datasetForgeScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.forge_boundary || "dataset manifests only")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.manifest_count || 0)}</strong><small>manifests</small></span>
        <span><strong>${escapeHtml(scorecard.ready_count || 0)}</strong><small>ready</small></span>
        <span><strong>${escapeHtml(scorecard.blocked_count || 0)}</strong><small>blocked</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(latest.dataset_manifest_id || scorecard.adapter_boundary || "No dataset manifests forged")}</div>
    <div class="completion-scope">Latest build action: ${escapeHtml(latestBuild.dataset_manifest_id ? `${latestBuild.dataset_manifest_id} -> ${latestBuild.status || "manifest"}` : "No DatasetForge manifest built in this browser session")}</div>
    <div class="completion-scope">Handoff source: ${escapeHtml(latestHandoff.endpoint ? `${latestHandoff.method || "POST"} ${latestHandoff.endpoint} | build allowed ${latestHandoff.build_allowed ? "true" : "false"}` : "No Dataset Radar handoff loaded")}</div>
    <div class="completion-scope">Lineage split policy: train ${(lineageSplitPolicy.train_source_ids || []).join(", ") || "none"} | context ${(lineageSplitPolicy.teacher_context_only_source_ids || []).join(", ") || "none"} | sealed eval blocked from train ${(lineageSplitPolicy.sealed_eval_source_ids || []).join(", ") || "none"}</div>
    <div class="completion-scope">Training review gate: ${escapeHtml(trainingReviewGate.gate_id || "dataset_radar_training_review_gate")} | ${trainingReviewGate.allowed === false ? "needs review" : "allowed"} | blocked ${(trainingReviewGate.blocked_source_ids || []).join(", ") || "none"}</div>
    ${scorecardLaneGrid((trainingReviewGate.blockers || []).slice(0, 6).map((blocker) => ({
      lane_id: blocker.source_id || blocker.review_packet_id || "training-review-blocker",
      label: `${blocker.review_state || "review"} | ${(blocker.blocking_fields || []).join(", ") || "no fields"} | ${blocker.reason || "review required"}`,
      state: "research-candidate",
    })))}
    <div class="completion-scope">Manifest-time source review packets: ${escapeHtml(reviewPackets.length)} packet${reviewPackets.length === 1 ? "" : "s"}</div>
    ${scorecardLaneGrid(reviewPackets.slice(0, 6).map((packet) => {
      const review = packet.review_required_packet || {};
      const blockingFields = review.blocking_fields || [];
      return {
        lane_id: packet.dataset_radar_source_id || packet.source_id || review.dataset_id || "dataset-radar-source",
        label: `${review.review_state || "review"} | training promotion ${review.training_promotion_allowed ? "allowed" : "blocked"} | blocking ${blockingFields.join(", ") || "none"}`,
        state: review.training_promotion_allowed ? "live-bound" : review.review_state === "complete" ? "shadow-only" : "research-candidate",
      };
    }))}
    <div class="completion-scope">Review-blocked Dataset Flow lineage: ${escapeHtml(reviewBlockedLineage.length)} source${reviewBlockedLineage.length === 1 ? "" : "s"}</div>
    ${scorecardLaneGrid(reviewBlockedLineage.slice(0, 6).map((row) => ({
      lane_id: row.source_id || row.request_source_id || row.dataset_manifest_id,
      label: `${row.source_review_state || "review"} | training promotion ${row.training_promotion_allowed ? "allowed" : "blocked"} | blocking ${(row.review_blocking_fields || []).join(", ") || "none"}`,
      state: row.training_promotion_allowed ? "live-bound" : "research-candidate",
    })))}
    ${scorecardLaneGrid(manifests.slice(0, 6).map((manifest) => ({
      lane_id: manifest.dataset_manifest_id,
      label: `${manifest.dataset?.example_count || 0} examples | ${manifest.dataset?.license_status || "unknown"} | ${manifest.task_type || "dataset"}`,
      state: manifest.status || "static-canon",
    })))}
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderKnowledgeArtifactsScorecard() {
  const scorecard = state.knowledgeArtifacts || {};
  const latest = scorecard.latest_artifact || {};
  const artifacts = scorecard.artifacts || [];
  const consumers = scorecard.code_backed_consumers || [];
  const actions = scorecard.operator_actions || {};
  const sourceRefGate = latest.source_ref_security_gate || {};
  const sourceRefGateSummary = scorecard.source_ref_gate_summary || {};
  const blockedSourceRefs = latest.blocked_source_refs || sourceRefGate.blocked_source_refs || [];
  const latestTrustPreview = latest.artifact_trust_preview || {};
  const trustPreviewSummary = scorecard.artifact_trust_preview_summary || {};
  const latestTrustScan = state.knowledgeArtifactTrustScan || {};
  const activeRuntimeBlockers = scorecard.active_runtime_blockers || [];
  const runtimeGateCoverage = scorecard.downstream_runtime_gate_coverage || {};
  const latestQueryEvent = scorecard.latest_query_event || {};
  const actionTokens = Object.entries(actions)
    .map(([key, action]) => `<span class="token">${escapeHtml(pretty(key))}: ${escapeHtml(action.method || "")} ${escapeHtml(action.endpoint || action.endpoint_template || "")}</span>`)
    .join("");
  fill(dom.knowledgeArtifactsScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.boundary || "compiled artifacts only; no model or prompt mutation")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.artifact_count || 0)}</strong><small>artifacts</small></span>
        <span><strong>${escapeHtml(scorecard.stale_count || 0)}</strong><small>stale</small></span>
        <span><strong>${escapeHtml(latest.conflict_count || 0)}</strong><small>conflicts</small></span>
        <span><strong>${escapeHtml(latest.excluded_source_count || 0)}</strong><small>permission filtered</small></span>
        <span><strong>${escapeHtml(sourceRefGate.blocked_count || latest.blocked_source_ref_count || 0)}</strong><small>blocked source refs</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(scorecard.raw_retrieval_boundary || "Raw retrieval remains fallback")}</div>
    <div class="completion-scope">Ledger ${escapeHtml(scorecard.ledger_ref || "PB-2026-05-05-080")} | status ${escapeHtml(scorecard.status || "candidate")} | promoted ${scorecard.promotion_readiness?.promoted ? "yes" : "no"}</div>
    <div class="completion-scope">Latest artifact: ${escapeHtml(latest.artifact_id || "No compiled artifact yet")}</div>
    <div class="completion-scope">KAC source-ref security gate: ${escapeHtml(sourceRefGate.allowed === false ? "blocked" : "clear")} | requested ${escapeHtml(sourceRefGate.requested_count || 0)} | blocked ${escapeHtml(sourceRefGate.blocked_count || 0)}</div>
    <div class="completion-scope">KAC source-ref gate summary: blocked ${escapeHtml(sourceRefGateSummary.latest_blocked_count || 0)} | allowed ${escapeHtml(sourceRefGateSummary.latest_allowed_count || 0)} | reasons ${(sourceRefGateSummary.latest_blocked_reasons || []).map((reason) => escapeHtml(reason)).join(", ") || "none"}</div>
    <div class="completion-scope">Automatic KAC artifact trust preview: ${escapeHtml(latestTrustPreview.status || "not available")} | ${escapeHtml(latestTrustPreview.trust_decision || "compile has not produced a preview yet")}</div>
    <div class="completion-scope">KAC trust-preview summary: ${escapeHtml(trustPreviewSummary.latest_status || "not scanned")} | ${escapeHtml(trustPreviewSummary.latest_decision || "no decision")} | persisted ${trustPreviewSummary.persisted ? "yes" : "no"}</div>
    <div class="completion-scope">KAC active runtime blockers: ${activeRuntimeBlockers.map((blocker) => escapeHtml(blocker)).join(", ") || "none"}</div>
    <div class="completion-scope">KAC query history: ${escapeHtml(scorecard.query_event_count || 0)} events | latest ${escapeHtml(latestQueryEvent.fallback_state || "none")} | runtime allowed ${latestQueryEvent.runtime_context_allowed ? "yes" : "no"} | ${escapeHtml(latestQueryEvent.event_id || "no query event")}</div>
    <div class="completion-scope">KAC downstream runtime gate coverage: ${escapeHtml(runtimeGateCoverage.gated_consumer_count || 0)}/${escapeHtml(runtimeGateCoverage.required_consumer_count || 0)} runtime consumers gated | code-enforced ${escapeHtml(runtimeGateCoverage.enforced_consumer_count || 0)}/${escapeHtml(runtimeGateCoverage.required_consumer_count || 0)} | all gated ${runtimeGateCoverage.all_runtime_consumers_gated ? "yes" : "no"} | proofs ${escapeHtml(runtimeGateCoverage.proof_ref_count || 0)} | ${escapeHtml(runtimeGateCoverage.gate_source || "KnowledgeArtifactCompiler.query")}</div>
    <div class="completion-scope">Latest KAC artifact trust scan: ${escapeHtml(latestTrustScan.status || "not run")} | ${escapeHtml(latestTrustScan.trust_decision || "scan latest artifact to update Artifact Trust replay")}</div>
    <div class="token-grid">
      <button type="button" data-kac-artifact-trust-scan="${escapeAttr(latest.artifact_id || "")}" title="Scan the latest KAC artifact through Artifact Trust">Scan KAC Artifact Trust</button>
    </div>
    ${scorecardLaneGrid(blockedSourceRefs.slice(0, 6).map((blocked) => ({
      lane_id: blocked.source_ref || "blocked-source-ref",
      label: `${blocked.reason || "source_ref_blocked"} | blocked source refs | ${blocked.source_ref_gate || "blocked_before_read"}`,
      state: "blocked",
    })))}
    ${scorecardLaneGrid(artifacts.slice(0, 6).map((artifact) => ({
      lane_id: artifact.artifact_id,
      label: `${artifact.task_family || "task"} | sources ${artifact.source_count || 0} | conflicts ${artifact.conflict_count || 0} | valid ${artifact.validation?.valid ? "yes" : "no"}`,
      state: artifact.status || "candidate",
    })))}
    <div class="completion-scope">KAC code-backed consumers</div>
    ${scorecardLaneGrid(consumers.map((consumer) => ({
      lane_id: consumer.consumer_id,
      label: `${consumer.boundary || "refs-only"} | mutation ${consumer.mutation_allowed ? "allowed" : "blocked"} | requires KRC runtime context allowed ${consumer.requires_krc_runtime_context_allowed ? "yes" : "no"} | blocks raw fallback ${consumer.blocks_raw_retrieval_fallback_context ? "yes" : "no"} | ${consumer.enforcement_state === "blocks_disallowed_krc_evidence" ? "code-enforced" : "replay-only"} | proofs ${(consumer.proof_refs || []).length}`,
      state: consumer.mutation_allowed ? "blocked" : "candidate",
    })))}
    <div class="completion-scope">Knowledge Artifact Compiler controls</div>
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
    <div class="token-grid">${actionTokens}</div>
  `);
}

function renderDatasetRadarScorecard() {
  const scorecard = state.datasetRadar || {};
  const stateCounts = scorecard.state_counts || {};
  const lineage = scorecard.coder_expert_lineage || [];
  const latestCandidates = scorecard.latest_candidates || [];
  const gatePreviews = scorecard.candidate_gate_previews || [];
  const refreshHistory = scorecard.refresh_history || [];
  const refreshBatchHistory = scorecard.refresh_batch_history || [];
  const materialRequests = scorecard.material_request_history || [];
  const candidateReviews = scorecard.candidate_review_history || [];
  const presets = scorecard.refresh_presets || [];
  const freshnessSummary = scorecard.freshness_summary || {};
  const refreshDueSources = scorecard.refresh_due_sources || [];
  const freshnessWarnings = scorecard.source_freshness_warnings || [];
  const refreshRunFreshness = scorecard.refresh_run_freshness || {};
  const refreshRecommendations = scorecard.refresh_recommendations || [];
  const refresh = state.datasetRadarRefresh || {};
  const batch = state.datasetRadarBatch || {};
  const sessionReview = state.datasetRadarCandidateReview || {};
  const sessionMaterialRequest = state.datasetRadarMaterialRequest || {};
  const sourceDetail = state.datasetRadarSourceDetail || {};
  const sourceReviewPacket = sourceDetail.review_required_packet || {};
  const sourceReviewFields = sourceReviewPacket.fields || [];
  const latestForgeHandoff = sessionMaterialRequest.dataset_forge_handoff || scorecard.latest_material_request?.dataset_forge_handoff || {};
  const actions = scorecard.operator_actions || {};
  const stateTokens = Object.entries(stateCounts)
    .slice(0, 8)
    .map(([key, value]) => `<span class="token">${escapeHtml(pretty(key))}: ${escapeHtml(value)}</span>`)
    .join("");
  const actionTokens = Object.entries(actions)
    .map(([key, action]) => `<span class="token">${escapeHtml(pretty(key))}: ${escapeHtml(action.method || "")} ${escapeHtml(action.endpoint || action.endpoint_template || "")}</span>`)
    .join("");
  fill(dom.datasetRadarScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.teacher_access_rule || "teacher councils request material through Dataset Radar only")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.source_count || 0)}</strong><small>sources</small></span>
        <span><strong>${escapeHtml(scorecard.approved_train_count || 0)}</strong><small>train ok</small></span>
        <span><strong>${escapeHtml(scorecard.blocked_count || 0)}</strong><small>blocked</small></span>
        <span><strong>${escapeHtml(scorecard.candidate_gate_blocked_count || 0)}</strong><small>candidate gate blocks</small></span>
        <span><strong>${escapeHtml(scorecard.candidate_count || latestCandidates.length || 0)}</strong><small>candidates</small></span>
        <span><strong>${escapeHtml(scorecard.refresh_warning_count || 0)}</strong><small>warnings</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(scorecard.boundary || "read-only-discover-score-gate-display-no-download-no-training")}</div>
    <div class="completion-scope">Freshness Radar: ${escapeHtml(freshnessSummary.refresh_due_count || 0)} source refreshes due; latest refresh ${escapeHtml(refreshRunFreshness.refresh_due ? "due" : "current")}</div>
    <div class="mini-metrics">
      <span><strong>${escapeHtml(freshnessSummary.current_count || 0)}</strong><small>current</small></span>
      <span><strong>${escapeHtml(freshnessSummary.stale_count || 0)}</strong><small>stale</small></span>
      <span><strong>${escapeHtml(freshnessSummary.manual_review_count || 0)}</strong><small>manual</small></span>
      <span><strong>${escapeHtml(freshnessSummary.invalid_count || 0)}</strong><small>invalid</small></span>
    </div>
    ${scorecardLaneGrid(refreshDueSources.slice(0, 5).map((source) => ({
      lane_id: source.dataset_id,
      label: `${source.freshness_status || "freshness"} | ${source.cadence || "cadence"} | overdue ${source.days_overdue ?? 0}d | ${source.reason || "refresh due"}`,
      state: source.severity === "high" ? "blocked" : "research-candidate",
    })))}
    <div class="token-grid">${refreshDueSources.slice(0, 5).map((source) => `<button type="button" data-dataset-radar-detail="${escapeAttr(source.dataset_id)}" title="Inspect due Dataset Radar source detail">Inspect Due Source</button>`).join("")}</div>
    <div class="completion-scope">Freshness Warnings</div>
    ${scorecardLaneGrid(freshnessWarnings.slice(0, 5).map((warning) => ({
      lane_id: warning.warning_id,
      label: `${warning.dataset_id || "dataset"} | ${warning.reason || "warning"}`,
      state: warning.severity === "high" ? "blocked" : "research-candidate",
    })))}
    <div class="completion-scope">Refresh Recommendations</div>
    ${scorecardLaneGrid(refreshRecommendations.slice(0, 5).map((recommendation) => ({
      lane_id: recommendation.recommendation_id,
      label: `${recommendation.endpoint || "endpoint"} | ${(recommendation.preset_ids || []).join(", ") || "custom query"} | ${(recommendation.due_source_ids || []).slice(0, 4).join(", ") || "no due sources"}`,
      state: recommendation.auto_execute_allowed ? "blocked" : "research-candidate",
    })))}
    <div class="token-grid">${refreshRecommendations.slice(0, 5).flatMap((recommendation) => (recommendation.due_source_ids || []).slice(0, 3)).map((datasetId) => `<button type="button" data-dataset-radar-detail="${escapeAttr(datasetId)}" title="Inspect refresh recommendation source detail">Inspect Recommended Source</button>`).join("")}</div>
    ${scorecardLaneGrid(lineage.slice(0, 6).map((source) => ({
      lane_id: source.dataset_id,
      label: `${source.license_state || "license"} | ${(source.allowed_uses || []).slice(0, 3).join(", ") || "no uses"} | ${(source.curriculum_stages || []).slice(0, 2).join(", ") || "curriculum"}`,
      state: source.license_state === "approved_train" ? "live-bound" : source.license_state === "sealed_eval_only" ? "shadow-only" : "research-candidate",
    })))}
    <div class="completion-scope">Replay Artifacts</div>
    ${scorecardLaneGrid(refreshHistory.slice(0, 5).map((run) => ({
      lane_id: run.refresh_run_id,
      label: `${run.candidate_count || 0} candidates | ${run.replay?.artifact_ref || "no artifact"} | ${run.replay?.event_log_ref || "no event_log_ref"}`,
      state: run.auto_approval_allowed ? "blocked" : "live-bound",
    })))}
    <div class="completion-scope">Preset Batch Replay</div>
    ${scorecardLaneGrid(refreshBatchHistory.slice(0, 4).map((run) => ({
      lane_id: run.batch_id,
      label: `${run.preset_count || 0} presets | ${run.candidate_count || 0} candidates | ${run.replay?.artifact_ref || "no batch artifact"}`,
      state: run.auto_approval_allowed ? "blocked" : "live-bound",
    })))}
    <div class="completion-scope">Latest refresh: ${escapeHtml(refresh.candidate_count !== undefined ? `${refresh.candidate_count} candidates, auto approval disabled` : "No operator refresh run in this browser session")}</div>
    <div class="completion-scope">Latest batch: ${escapeHtml(batch.batch_id ? `${batch.preset_count || 0} presets, ${batch.candidate_count || 0} candidates` : "No batch refresh run in this browser session")}</div>
    <div class="completion-scope">Latest review action: ${escapeHtml(sessionReview.candidate_review_id ? `${sessionReview.dataset_id || "candidate"} -> ${sessionReview.applied_state || "pending"}` : "No candidate review action in this browser session")}</div>
    <div class="completion-scope">Latest material request: ${escapeHtml(sessionMaterialRequest.material_request_id ? `${sessionMaterialRequest.requested_split || "split"} for ${sessionMaterialRequest.target_node || "target"} with ${(sessionMaterialRequest.approved_source_ids || []).length} approved` : "No material request action in this browser session")}</div>
    <div class="completion-scope">DatasetForge handoff: ${escapeHtml(latestForgeHandoff.endpoint ? `${latestForgeHandoff.method || "POST"} ${latestForgeHandoff.endpoint} | auto execute ${latestForgeHandoff.auto_execute_allowed ? "allowed" : "blocked"}` : "No DatasetForge handoff packet in this browser session")}</div>
    <div class="completion-scope">Latest source detail: ${escapeHtml(sourceDetail.dataset_id ? `${sourceDetail.dataset_id} | ${sourceDetail.source_kind || "source"} | ${(sourceDetail.material_request_usage || []).length} material requests` : "No source detail lookup in this browser session")}</div>
    <div class="completion-scope">Source review packet: ${escapeHtml(sourceReviewPacket.packet_id ? `${sourceReviewPacket.review_state || "review"} | training promotion ${sourceReviewPacket.training_promotion_allowed ? "allowed" : "blocked"} | blocking ${(sourceReviewPacket.blocking_fields || []).join(", ") || "none"}` : "No source review packet loaded")}</div>
    ${scorecardLaneGrid(sourceReviewFields.slice(0, 6).map((field) => ({
      lane_id: field.field,
      label: `${field.current_value || "unknown"} | ${(field.accepted_evidence || []).slice(0, 2).join(", ") || field.reason || "review evidence"}`,
      state: field.status === "satisfied" ? "live-bound" : field.status === "blocked" ? "blocked" : "research-candidate",
    })))}
    <div class="completion-scope">Review Priority Ranking</div>
    <div class="scorecard-mini-grid">${latestCandidates.slice(0, 6).map((candidate) => {
      const signals = candidate.quality_signals || {};
      const candidateState = candidate.auto_approved ? "blocked" : candidate.license_state === "pending_provenance_review" ? "research-candidate" : "blocked";
      return `
        <article class="runtime-scorecard-card">
          <div class="metric-head">
            <strong>${escapeHtml(candidate.dataset_id)}</strong>
            <span class="state-pill ${escapeHtml(candidateState)}">${escapeHtml(pretty(candidateState))}</span>
          </div>
          <small>${escapeHtml(`score ${candidate.review_score ?? "n/a"} | ${signals.review_priority || "unranked"} | target ${signals.target_fit_signal ?? 0} | freshness ${signals.freshness_signal ?? 0}`)}</small>
          <button type="button" data-dataset-radar-detail="${escapeAttr(candidate.dataset_id)}" title="Inspect Dataset Radar source detail replay">Inspect Source</button>
        </article>
      `;
    }).join("")}</div>
    <div class="completion-scope">Candidate Gate Preview</div>
    ${scorecardLaneGrid(gatePreviews.slice(0, 5).map((preview) => ({
      lane_id: preview.dataset_id,
      label: `${preview.license_state || "unknown"} | ${(preview.gates || []).map((gate) => `${gate.split}:${gate.allowed ? "allow" : "block"}`).slice(0, 4).join(", ")}`,
      state: preview.source_kind === "canonical_source" ? "live-bound" : "blocked",
    })))}
    <div class="completion-scope">Candidate Reviews</div>
    ${scorecardLaneGrid(candidateReviews.slice(0, 5).map((review) => ({
      lane_id: review.candidate_review_id,
      label: `${review.dataset_id || "dataset"} | ${review.applied_state || "pending"} | ${(review.allowed_uses || []).join(", ") || "no use"}`,
      state: review.decision === "blocked_training_approval" || String(review.applied_state || "").startsWith("blocked_") ? "blocked" : "research-candidate",
    })))}
    <div class="completion-scope">Teacher Material Requests</div>
    ${scorecardLaneGrid(materialRequests.slice(0, 5).map((request) => ({
      lane_id: request.material_request_id,
      label: `${request.teacher_ref || "teacher"} | ${request.target_node || "target"} | ${(request.approved_source_ids || []).length} approved`,
      state: request.auto_download_allowed ? "blocked" : "live-bound",
    })))}
    <div class="completion-scope">Target-Node Presets</div>
    <div class="token-grid">${presets.map((preset) => `<span class="token">${escapeHtml(preset.label || preset.preset_id)}: ${escapeHtml((preset.target_nodes || []).slice(0, 3).join(", "))}</span>`).join("")}</div>
    <div class="token-grid">${stateTokens}</div>
    <div class="token-grid">${actionTokens}</div>
  `);
}

function renderEvalRegistryScorecard() {
  const scorecard = state.evalRegistry || {};
  const latest = scorecard.latest_suite || {};
  const latestShadowRun = scorecard.latest_shadow_run || {};
  const upstream_lifecycle_gate = latestShadowRun.upstream_lifecycle_gate || {};
  const suites = scorecard.suites || [];
  fill(dom.evalRegistryScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.promotion_boundary || "held-out eval gate before promotion")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.suite_count || 0)}</strong><small>suites</small></span>
        <span><strong>${escapeHtml(scorecard.active_count || 0)}</strong><small>active</small></span>
        <span><strong>${escapeHtml(scorecard.blocked_count || 0)}</strong><small>blocked</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(latest.suite_id || "No eval suites registered")}</div>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Eval upstream lifecycle gate</strong>
        <span class="state-pill ${latestShadowRun.promotion_allowed ? "live-bound" : "blocked"}">${latestShadowRun.promotion_allowed ? "promotion clear" : "promotion blocked"}</span>
      </div>
      <small>${escapeHtml(upstream_lifecycle_gate.lifecycle_ref || latestShadowRun.run_id || "No upstream lifecycle gate recorded")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(upstream_lifecycle_gate.lifecycle_status || "unknown")}</strong><small>upstream lifecycle gate</small></span>
        <span><strong>${escapeHtml(upstream_lifecycle_gate.growth_engine_gate_allowed === false ? "blocked" : "clear")}</strong><small>growth</small></span>
        <span><strong>${escapeHtml(upstream_lifecycle_gate.artifact_trust_promotion_allowed === false ? "blocked" : "clear")}</strong><small>artifact trust</small></span>
        <span><strong>${escapeHtml(upstream_lifecycle_gate.blockers?.length || 0)}</strong><small>blockers</small></span>
      </div>
    </article>
    ${scorecardLaneGrid(suites.slice(0, 6).map((suite) => ({
      lane_id: suite.suite_id,
      label: `${suite.suite_type || "eval"} | ${(suite.benchmark_refs || []).slice(0, 3).join(", ") || "held-out"} | ${suite.promotion_gate || "gate"}`,
      state: suite.status || "static-canon",
    })))}
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderArtifactTrustRegistryScorecard() {
  const scorecard = state.artifactTrustRegistry || {};
  const latest = scorecard.latest_scan || {};
  const scans = scorecard.scans || [];
  fill(dom.artifactTrustRegistryScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.supply_chain_boundary || "artifact trust gate")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.scan_count || 0)}</strong><small>scans</small></span>
        <span><strong>${escapeHtml(scorecard.trusted_count || 0)}</strong><small>trusted</small></span>
        <span><strong>${escapeHtml(scorecard.quarantined_count || 0)}</strong><small>quarantine</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(latest.artifact_id || "No artifact scans recorded")}</div>
    ${scorecardLaneGrid(scans.slice(0, 6).map((scan) => ({
      lane_id: scan.artifact_id,
      label: `${scan.artifact_type || "artifact"} | ${scan.format || "unknown"} | ${scan.trust_decision || "review"}`,
      state: scan.status || "static-canon",
    })))}
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function releaseWrapperActionButton(action, label, ref) {
  const disabled = ref ? "" : " disabled";
  return `<button type="button" data-release-wrapper-action="${escapeHtml(action)}"${disabled}>${escapeHtml(label)}</button>`;
}

function isUniversalEvolutionStatusAvailable(evolution) {
  if (!evolution || typeof evolution !== "object" || Array.isArray(evolution)) {
    return false;
  }
  const coverage = evolution.coverage;
  return evolution.authority === "NexusBrain"
    && coverage
    && typeof coverage === "object"
    && !Array.isArray(coverage)
    && Number.isInteger(coverage.registered_unit_total)
    && coverage.registered_unit_total >= 0
    && Number.isInteger(coverage.covered_unit_total)
    && coverage.covered_unit_total >= 0
    && coverage.covered_unit_total <= coverage.registered_unit_total
    && Array.isArray(coverage.uncovered_unit_refs)
    && coverage.uncovered_unit_refs.every((unitRef) => typeof unitRef === "string")
    && coverage.covered_unit_total + coverage.uncovered_unit_refs.length === coverage.registered_unit_total
    && typeof coverage.universal_coverage_complete === "boolean"
    && Number.isInteger(evolution.open_pressure_count)
    && evolution.open_pressure_count >= 0
    && Array.isArray(evolution.top_pressures)
    && evolution.top_pressures.every((pressure) => pressure && typeof pressure.pressure_id === "string")
    && evolution.top_pressures.length === Math.min(evolution.open_pressure_count, 5)
    && Array.isArray(evolution.missing_or_unverified_prerequisites)
    && evolution.missing_or_unverified_prerequisites.every((name) => typeof name === "string")
    && (evolution.last_event_sha256 === null || typeof evolution.last_event_sha256 === "string")
    && evolution.claim_boundary === "registry-and-evidence-state-only; no candidate, experiment, promotion, native-model-birth, or frontier-superiority claim"
    && evolution.mutation_boundary === "read-only-no-protected-state-mutation"
    && coverage.claim_boundary === "legacy-lane-coverage-is-not-universal-organism-coverage";
}

function renderUniversalEvolutionCard(evolution) {
  if (!isUniversalEvolutionStatusAvailable(evolution)) {
    return `
      <article class="runtime-scorecard-card universal-evolution-card evolution-status-unavailable">
        <div class="metric-head">
          <strong>Universal Evolution</strong>
          <span class="state-pill shadow-only">unavailable / unverified</span>
        </div>
        <small>Read-only evolution telemetry is unavailable/unverified.</small>
        <small>legacy-lane-coverage-is-not-universal-organism-coverage</small>
        <div class="evolution-prerequisite-gaps">coverage, pressure, and prerequisite state was not observed</div>
      </article>
    `;
  }
  const coverage = evolution.coverage;
  const topPressure = evolution.top_pressures[0] || null;
  const prerequisiteGaps = evolution.missing_or_unverified_prerequisites;
  return `
    <article class="runtime-scorecard-card universal-evolution-card">
      <div class="metric-head">
        <strong>Universal Evolution</strong>
        <span class="state-pill shadow-only">${escapeHtml(evolution.authority)}</span>
      </div>
      <small>Read-only status projection; legacy-lane-coverage-is-not-universal-organism-coverage.</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(coverage.registered_unit_total)}</strong><small>registered_unit_count</small></span>
        <span><strong>${escapeHtml(coverage.covered_unit_total)}</strong><small>covered_unit_count</small></span>
        <span><strong>${escapeHtml(coverage.uncovered_unit_refs.length)}</strong><small>uncovered_unit_count</small></span>
        <span><strong>${escapeHtml(evolution.open_pressure_count)}</strong><small>open pressure count</small></span>
        <span><strong>${escapeHtml(topPressure?.pressure_id || "not-applicable-no-open-pressures")}</strong><small>top pressure ID</small></span>
        <span><strong>${escapeHtml(evolution.last_event_sha256 || "not-recorded-in-loaded-status")}</strong><small>last event hash</small></span>
        <span><strong>${escapeHtml(coverage.universal_coverage_complete === false ? "false" : "not-established")}</strong><small>universal_coverage_complete</small></span>
      </div>
      <div class="evolution-prerequisite-gaps">missing or unverified prerequisites: ${escapeHtml(prerequisiteGaps.join(", ") || "none-observed-in-loaded-status")}</div>
      <div class="completion-scope">${escapeHtml(evolution.claim_boundary)} | ${escapeHtml(evolution.mutation_boundary)}</div>
    </article>
  `;
}

function renderAutonomousUpdatesScorecard() {
  const scorecard = state.autonomousUpdates || {};
  const releaseRuntime = state.releaseHarnessRuntime || state.releaseWrapperRuntime || {};
  const evolution = state.releaseWrapperStatus?.evolution;
  const releaseHarness = releaseRuntime.release_harness || {};
  const releaseReadiness = state.releaseWrapperReadiness || {};
  const releaseTelemetry = state.releaseWrapperTelemetry || releaseRuntime.live_wrapper_telemetry || {};
  const forwardPassCoverage = releaseRuntime.forward_pass_coverage || releaseTelemetry.forward_pass_coverage || {};
  const nexusbrainRuntimeCycle = releaseRuntime.nexusbrain_runtime_cycle
    || releaseTelemetry.nexusbrain_runtime_cycle
    || {};
  const wholeSystemHeartbeat = releaseRuntime.whole_system_heartbeat
    || state.releaseWrapperStatus?.whole_system_heartbeat
    || {};
  const wholeSystemHeartbeatTick = releaseRuntime.whole_system_heartbeat_tick
    || wholeSystemHeartbeat.latest_tick
    || {};
  const forwardPassMatrix = releaseRuntime.whole_system_forward_pass_enforcement_matrix
    || state.releaseWrapperStatus?.whole_system_forward_pass_enforcement_matrix
    || state.controlPanel?.release_wrapper_forward_pass_enforcement_matrix
    || {};
  const federatedPacketOutbox = releaseRuntime.federated_packet_outbox || {};
  const privacyConsent = releaseRuntime.privacy_consent
    || state.releaseWrapperStatus?.privacy_consent
    || state.controlPanel?.release_wrapper_privacy_consent
    || {};
  const federatedPacketInbox = releaseRuntime.federated_packet_inbox || {};
  const canonicalAoCoverage = releaseRuntime.canonical_ao_coverage || {};
  const domainAoRouting = releaseRuntime.domain_ao_routing || {};
  const domainTeacherEval = releaseRuntime.domain_teacher_eval_handoff || {};
  const cluster9TeacherReconciliation = releaseRuntime.cluster9_teacher_reconciliation
    || state.cluster9TeacherReconciliation
    || state.controlPanel?.cluster9_teacher_reconciliation
    || {};
  const contextWindowPosture = releaseRuntime.context_window_posture || {};
  const contextCapability = releaseRuntime.context_capability_envelope || {};
  const providerReadiness = releaseRuntime.provider_readiness || {};
  const firstRunReadiness = releaseRuntime.first_run_readiness || state.releaseWrapperStatus?.first_run_readiness || {};
  const releaseManifestRollup = releaseRuntime.release_manifest_status_rollup || state.releaseWrapperStatus?.release_manifest_status_rollup || {};
  const productionSpineReleaseLifecycle = releaseRuntime.production_spine_release_lifecycle || state.releaseWrapperStatus?.production_spine_release_lifecycle || {};
  const developmentalReleaseContract = releaseRuntime.developmental_release_contract
    || state.releaseWrapperStatus?.developmental_release_contract
    || state.controlPanel?.release_wrapper_developmental_release_contract
    || {};
  const latestProductionSpineReleaseLifecycle = productionSpineReleaseLifecycle.latest_run || {};
  const productionSpineReleaseLifecycleApproval = latestProductionSpineReleaseLifecycle.admin_approval || productionSpineReleaseLifecycle.admin_approval || {};
  const productionSpineReleaseLifecycleGovernance = latestProductionSpineReleaseLifecycle.authority_evidence_tool_governance || {};
  const productionSpineReleaseLifecycleRollback = productionSpineReleaseLifecycle.latest_rollback || {};
  const firstRunProduction = firstRunReadiness.production_spine || {};
  const firstRunScope = firstRunReadiness.product_scope || "wrapper-session";
  const bootSupervisor = releaseRuntime.boot_supervisor || state.releaseWrapperStatus?.boot_supervisor || state.controlPanel?.release_wrapper_boot_supervisor || {};
  const releaseProductSmoke = releaseRuntime.release_product_smoke
    || state.releaseWrapperStatus?.release_product_smoke
    || state.controlPanel?.release_wrapper_release_product_smoke
    || {};
  const releaseRunHistory = releaseRuntime.release_run_history
    || state.releaseWrapperStatus?.release_run_history
    || state.controlPanel?.release_wrapper_release_run_history
    || {};
  const nativeHiveHeartbeatWatchdog = releaseRuntime.native_hive_heartbeat_watchdog
    || state.releaseWrapperStatus?.native_hive_heartbeat_watchdog
    || state.controlPanel?.release_wrapper_native_hive_heartbeat_watchdog
    || {};
  const releaseHealthHeartbeat = releaseRuntime.release_health_heartbeat
    || state.releaseWrapperStatus?.release_health_heartbeat
    || state.controlPanel?.release_wrapper_release_health_heartbeat
    || {};
  const releaseHealthHeartbeatLoop = releaseRuntime.release_health_heartbeat_loop
    || state.releaseWrapperStatus?.release_health_heartbeat_loop
    || state.controlPanel?.release_wrapper_release_health_heartbeat_loop
    || {};
  const releaseHealthHeartbeatSupervisor = releaseRuntime.release_health_heartbeat_supervisor
    || state.releaseWrapperStatus?.release_health_heartbeat_supervisor
    || state.controlPanel?.release_wrapper_release_health_heartbeat_supervisor
    || {};
  const releaseHealthRepairHistory = releaseHealthHeartbeatSupervisor.repair_history || {};
  const latestHealthRepairEnvelopes = releaseHealthRepairHistory.latest_subsystem_repair_envelopes || [];
  const latestHealthRepairEnvelope = latestHealthRepairEnvelopes[0] || {};
  const projectHeartbeat = releaseRuntime.project_heartbeat
    || state.releaseWrapperStatus?.project_heartbeat
    || state.controlPanel?.project_heartbeat
    || {};
  const nativeHeartbeatRecoveryGovernance = projectHeartbeat.failure_recovery_governance || {};
  const canonContractLedger = releaseRuntime.canon_contract_ledger
    || state.releaseWrapperStatus?.canon_contract_ledger
    || state.controlPanel?.release_wrapper_canon_contract_ledger
    || {};
  const canonSourceManifest = canonContractLedger.source_manifest || {};
  const canonContractReceipts = releaseRuntime.canon_contract_receipts
    || state.releaseWrapperStatus?.canon_contract_receipts
    || state.controlPanel?.release_wrapper_canon_contract_receipts
    || {};
  const bootProductPath = bootSupervisor.evidence?.release_product_path || {};
  const bootProductPathAdmin = bootProductPath.admin_action_statuses || {};
  const bootProductPathFailureLearning = bootProductPath.failure_learning || {};
  const releaseLifecycle = state.releaseWrapperSessionLifecycle || {};
  const sessionHistory = releaseLifecycle.session_history || releaseRuntime.session_history || {};
  const telemetryAssimilation = releaseTelemetry.continuous_assimilation || {};
  const telemetryGrowth = releaseTelemetry.global_growth || {};
  const telemetryFederation = releaseTelemetry.federation || {};
  const telemetryProduction = releaseTelemetry.production_spine || {};
  const telemetryFailureLearning = releaseTelemetry.failure_learning || {};
  const telemetryEvents = releaseTelemetry.recent_events || [];
  const lifecycleSteps = releaseLifecycle.lifecycle_steps || [];
  const lifecycleStepCounts = releaseLifecycle.step_counts || {};
  const releaseManifestLifecycleStep = lifecycleSteps.find((step) => step.step_id === "release-manifest-rollup") || {};
  const releaseManifestMutationLabel = (
    releaseManifestLifecycleStep.release_mutation_allowed || releaseManifestRollup.release_mutation_allowed
  ) ? "active mutation allowed" : "active mutation blocked";
  const visibleLifecycleSteps = [
    ...lifecycleSteps.filter((step) => step.step_id === "release-manifest-rollup"),
    ...lifecycleSteps.filter((step) => step.step_id !== "release-manifest-rollup"),
  ].slice(0, 6);
  const selfRepairLedger = releaseLifecycle.self_repair_ledger || releaseRuntime.self_repair_ledger || state.releaseWrapperStatus?.self_repair_ledger || {};
  const latestSelfRepairGuard = selfRepairLedger.latest_ao_guard || {};
  const latestSelfRepairGuardReceipts = latestSelfRepairGuard.receipt_refs || [];
  const latestFederatedImportReceipt = federatedPacketInbox.latest_import?.operation_receipt || {};
  const operationReceiptRows = (forwardPassMatrix.entrypoints || []).filter((row) => row.operation_receipt?.receipt_id);
  const coveredOperationReceiptRows = operationReceiptRows.filter((row) => row.operation_receipt?.status === "covered");
  const selfRepairOperationReceiptActions = (selfRepairLedger.actions || []).filter((action) => action.operation_receipt?.receipt_id);
  const latestSelfRepairOperationReceipt = selfRepairOperationReceiptActions.slice(-1)[0]?.operation_receipt || {};
  const operationReceiptRefs = [
    latestFederatedImportReceipt.receipt_id,
    ...selfRepairOperationReceiptActions.map((action) => action.operation_receipt?.receipt_id),
  ].filter(Boolean);
  const releaseActionLane = state.releaseWrapperStatus?.operator_action_lane || {};
  const releaseActionStatuses = releaseActionLane.latest_action_statuses || {};
  const entrypoint = releaseRuntime.entrypoint || {};
  const globalGrowth = releaseRuntime.global_growth || {};
  const latestRuntimeGrowthReceipt = globalGrowth.latest_runtime_receipt || {};
  const runtimeGrowthPacket = latestRuntimeGrowthReceipt.federated_packet || {};
  const directNexusBrainForwardPass = releaseRuntime.direct_nexusbrain_forward_pass
    || state.controlPanel?.direct_nexusbrain_forward_pass
    || {};
  const dreamResearchQueue = releaseRuntime.dream_research_queue || {};
  const latestDreamResearchItem = dreamResearchQueue.latest_item || {};
  const latestDreamResearchMetadata = latestDreamResearchItem.metadata || {};
  const latestDreamResearchGovernance = latestDreamResearchItem.governance || {};
  const nativeRuntimeGrowthGovernance = releaseRuntime.native_runtime_growth_governance
    || state.releaseWrapperStatus?.native_runtime_growth_governance
    || releaseLifecycle.native_runtime_growth_governance
    || releaseLifecycle.autonomous_update_path?.native_runtime_growth_governance
    || {};
  const directNativeRuntimeGrowthGovernance = state.controlPanel?.direct_nexusbrain_native_growth_governance || {};
  const nativeRuntimeGrowthGovernanceStatuses = nativeRuntimeGrowthGovernance.latest_action_statuses || {};
  const nativeRuntimeGrowthSourceLabel = nativeRuntimeGrowthGovernance.direct_nexusbrain_generate
    ? "direct NexusBrain native growth"
    : "operator/manual native growth";
  const nativeRuntimeGrowthBridgeStatus = nativeRuntimeGrowthGovernance.native_hive_runtime_growth
    ? (nativeRuntimeGrowthGovernance.status || "queued")
    : latestDreamResearchMetadata.native_hive_runtime_growth ? "queued" : "not-queued";
  const nativeRuntimeGrowthReceiptLabel = nativeRuntimeGrowthGovernance.runtime_growth_receipt_id
    || latestDreamResearchMetadata.runtime_growth_receipt_id
    || "no-native-growth-receipt";
  const nativeRuntimeGrowthProposalStatus = nativeRuntimeGrowthGovernanceStatuses.proposal
    || latestDreamResearchGovernance.proposal_status
    || "not-generated";
  const nativeRuntimeGrowthEpisodeStatus = latestDreamResearchItem.latest_episode_status || "not-run";
  const nativeRuntimeGrowthSandboxStatus = nativeRuntimeGrowthGovernanceStatuses.sandbox_tests || "not-run";
  const nativeRuntimeGrowthApplyStatus = nativeRuntimeGrowthGovernanceStatuses.apply || "not-applied";
  const nativeRuntimeGrowthRollbackStatus = nativeRuntimeGrowthGovernanceStatuses.rollback || "not-rolled-back";
  const readinessChecks = releaseReadiness.readiness_checks || [];
  const passedReadiness = readinessChecks.filter((check) => check.status === "pass").length;
  const blockedReadiness = readinessChecks.filter((check) => check.status !== "pass").length;
  const latest = scorecard.latest_proposal || {};
  const latestSandbox = scorecard.latest_sandbox_test_evidence || {};
  const sandboxDiff = latestSandbox.diff_summary || {};
  const sandboxMode = latestSandbox.sandbox?.mode || "not-run";
  const sandboxModeLabel = sandboxMode === "isolated-filesystem-copy-allowlisted-pytest" ? "isolated filesystem" : sandboxMode;
  const upstream_eval_gate = latest.upstream_eval_gate || {};
  const upstream_lifecycle_gate = upstream_eval_gate.upstream_lifecycle_gate || {};
  const latestEvalReplay = latest.latest_eval_replay || {};
  const proposals = scorecard.proposals || [];
  fill(dom.autonomousUpdatesScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Release Harness runtime</strong>
        <span class="state-pill ${escapeHtml(entrypoint.runtime_state || "static-canon")}">${escapeHtml(pretty(entrypoint.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(releaseHarness.terminology_boundary || releaseRuntime.honest_status_label || "bootable-harness-entrypoint-awaiting-live-use")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(entrypoint.boot_target || "/ui/wrapper/")}</strong><small>entrypoint</small></span>
        <span><strong>${escapeHtml(releaseHarness.surface_id || "release-harness-runtime")}</strong><small>Harness surface</small></span>
        <span><strong>${escapeHtml(releaseHarness.legacy_surface_id || releaseRuntime.surface_id || "release-wrapper-runtime")}</strong><small>legacy compatibility key</small></span>
        <span><strong>${escapeHtml(cluster9TeacherReconciliation.node_count || 0)}</strong><small>Cluster 9 role nodes</small></span>
        <span><strong>${escapeHtml(cluster9TeacherReconciliation.pairing_gap_count || 0)}</strong><small>teacher pairing gaps</small></span>
        <span><strong>${escapeHtml(globalGrowth.global_captures || 0)}</strong><small>growth captures</small></span>
        <span><strong>${escapeHtml(globalGrowth.runtime_interaction_count || 0)}</strong><small>runtime growth bridge</small></span>
        <span><strong>${escapeHtml(latestRuntimeGrowthReceipt.surface_id || "no-runtime-growth-receipt")}</strong><small>latest runtime growth receipt</small></span>
        <span><strong>${escapeHtml(runtimeGrowthPacket.surface_id || "no-runtime-growth-packet")}</strong><small>shared growth fed packet</small></span>
        <span><strong>${escapeHtml(directNexusBrainForwardPass.status || "not-observed")}</strong><small>direct NexusBrain forward pass</small></span>
        <span><strong>${escapeHtml(directNexusBrainForwardPass.runtime_growth_federated_packet_id || "no-direct-brain-packet")}</strong><small>direct brain federated packet</small></span>
        <span><strong>${escapeHtml(directNexusBrainForwardPass.dream_signal_emitted ? "true" : "false")}</strong><small>direct brain dream signal</small></span>
        <span><strong>${escapeHtml(nativeRuntimeGrowthBridgeStatus)}</strong><small>native growth dream/research bridge</small></span>
        <span><strong>${escapeHtml(nativeRuntimeGrowthReceiptLabel)}</strong><small>native growth receipt</small></span>
        <span><strong>${escapeHtml(nativeRuntimeGrowthProposalStatus)}</strong><small>native growth proposal</small></span>
        <span><strong>${escapeHtml(nativeRuntimeGrowthEpisodeStatus)}</strong><small>native dream/research episode</small></span>
        <span><strong>${escapeHtml(nativeRuntimeGrowthSandboxStatus)}</strong><small>native growth sandbox</small></span>
        <span><strong>${escapeHtml(nativeRuntimeGrowthApplyStatus)}</strong><small>native growth safe apply</small></span>
        <span><strong>${escapeHtml(nativeRuntimeGrowthRollbackStatus)}</strong><small>native growth rollback</small></span>
        <span><strong>${escapeHtml(nativeRuntimeGrowthGovernance.status || "not-triggered")}</strong><small>native growth governance</small></span>
        <span><strong>${escapeHtml(directNativeRuntimeGrowthGovernance.status || "not-triggered")}</strong><small>direct NexusBrain native growth</small></span>
        <span><strong>${escapeHtml(nativeRuntimeGrowthGovernance.direct_nexusbrain_generate ? "true" : "false")}</strong><small>direct_nexusbrain_generate</small></span>
        <span><strong>${escapeHtml(nativeRuntimeGrowthSourceLabel)}</strong><small>native growth source</small></span>
        <span><strong>${escapeHtml(nativeHiveHeartbeatWatchdog.status || "blocked")}</strong><small>Heartbeat watchdog</small></span>
        <span><strong>${escapeHtml(nativeHiveHeartbeatWatchdog.runtime_state || "not-run")}</strong><small>native_hive_heartbeat_watchdog</small></span>
        <span><strong>${escapeHtml(releaseHealthHeartbeat.status || "not-run")}</strong><small>Release health heartbeat</small></span>
        <span><strong>${escapeHtml(releaseHealthHeartbeat.trigger || "not-run")}</strong><small>release_health_heartbeat</small></span>
        <span><strong>${escapeHtml(releaseHealthHeartbeatLoop.status || "not-run")}</strong><small>Release health loop</small></span>
        <span><strong>${escapeHtml(releaseHealthHeartbeatLoop.cycle_count || releaseHealthHeartbeatLoop.loop_count || 0)}</strong><small>release_health_heartbeat_loop</small></span>
        <span><strong>${escapeHtml(releaseHealthHeartbeatSupervisor.status || "disabled")}</strong><small>Release heartbeat supervisor</small></span>
        <span><strong>${escapeHtml(releaseHealthHeartbeatSupervisor.pulse_count || 0)}</strong><small>release health supervisor pulses</small></span>
        <span><strong>${escapeHtml(releaseHealthRepairHistory.latest_subsystem_repair_envelope_count || 0)}</strong><small>subsystem repair envelopes</small></span>
        <span><strong>${escapeHtml(latestHealthRepairEnvelope.honest_status_label || "not-run")}</strong><small>health repair envelope status</small></span>
        <span class="native-heartbeat-recovery-governance"><strong>${escapeHtml(nativeHeartbeatRecoveryGovernance.status || "not-emitted")}</strong><small>native heartbeat recovery governance</small></span>
        <span><strong>${escapeHtml(privacyConsent.status || "not-recorded")}</strong><small>privacy consent</small></span>
        <span><strong>${escapeHtml(privacyConsent.personal_data_training_opt_in ? "opted-in" : "default-off")}</strong><small>personal-data training</small></span>
        <span><strong>${escapeHtml(releaseRuntime.federated_packet_count || 0)}</strong><small>fed packets</small></span>
        <span><strong>${escapeHtml(federatedPacketOutbox.packet_count || releaseRuntime.federated_packet_count || 0)}</strong><small>federated packet outbox</small></span>
        <span><strong>${escapeHtml(federatedPacketInbox.import_count || 0)}</strong><small>federated packet inbox</small></span>
        <span><strong>${escapeHtml(forwardPassCoverage.latest_status || "not-run")}</strong><small>forward coverage</small></span>
        <span><strong>${escapeHtml(forwardPassCoverage.receipt_count || 0)}</strong><small>coverage receipts</small></span>
        <span><strong>${escapeHtml(nexusbrainRuntimeCycle.latest_status || "not-run")}</strong><small>NexusBrain runtime cycle</small></span>
        <span><strong>${escapeHtml(nexusbrainRuntimeCycle.receipt_count || 0)}</strong><small>NexusBrain cycle receipts</small></span>
        <span class="whole-system-heartbeat"><strong>${escapeHtml(wholeSystemHeartbeat.status || "not-observed")}</strong><small>Whole-system heartbeat</small></span>
        <span><strong>${escapeHtml(wholeSystemHeartbeat.tick_count || 0)}</strong><small>heartbeat ticks</small></span>
        <span><strong>${escapeHtml(wholeSystemHeartbeatTick.tick_id || "no-heartbeat-tick")}</strong><small>latest heartbeat tick</small></span>
        <span><strong>${escapeHtml(forwardPassMatrix.coverage_status || "partial")}</strong><small>forward-pass matrix</small></span>
        <span><strong>${escapeHtml(forwardPassMatrix.covered_entrypoint_count || 0)}/${escapeHtml(forwardPassMatrix.entrypoint_count || 0)}</strong><small>matrix entrypoints</small></span>
        <span><strong>${escapeHtml(operationReceiptRefs.length)}</strong><small>operation receipt refs</small></span>
        <span><strong>${escapeHtml(latestFederatedImportReceipt.status || "not-imported")}</strong><small>federated import receipt</small></span>
        <span><strong>${escapeHtml(selfRepairOperationReceiptActions.length)}</strong><small>self-repair operation receipts</small></span>
        <span><strong>${escapeHtml(canonicalAoCoverage.passed ? "passed" : "blocked")}</strong><small>canonical AO coverage</small></span>
        <span><strong>${escapeHtml(canonicalAoCoverage.receipt_count || 0)}</strong><small>canonical AO receipts</small></span>
        <span><strong>${escapeHtml(domainAoRouting.latest_domain_ao || "not-routed")}</strong><small>domain AO routing</small></span>
        <span><strong>${escapeHtml(domainAoRouting.route_count || 0)}</strong><small>domain AO receipts</small></span>
        <span><strong>${escapeHtml(domainTeacherEval.latest_domain_ao || "not-linked")}</strong><small>domain teacher/eval</small></span>
        <span><strong>${escapeHtml(domainTeacherEval.handoff_count || 0)}</strong><small>teacher/eval handoffs</small></span>
        <span><strong>${escapeHtml(domainTeacherEval.expert_growth_candidate_count || 0)}</strong><small>expert growth candidates</small></span>
        <span><strong>${escapeHtml(domainTeacherEval.latest_promotion_candidate_id || "none")}</strong><small>latest growth promotion</small></span>
        <span><strong>${escapeHtml(domainTeacherEval.latest_admin_eval_replay_status || "not-run")}</strong><small>expert growth admin replay</small></span>
        <span><strong>${escapeHtml(domainTeacherEval.latest_sandbox_takeover_evidence_status || "not-run")}</strong><small>expert takeover evidence</small></span>
        <span><strong>${escapeHtml(contextWindowPosture.status || "not-measured")}</strong><small>context window posture</small></span>
        <span><strong>${escapeHtml(contextWindowPosture.observed_effective_context_tokens || 0)}</strong><small>effective ctx tokens</small></span>
        <span><strong>${escapeHtml(contextCapability.canon_target_status || "not-measured")}</strong><small>context capability</small></span>
        <span><strong>${escapeHtml(contextCapability.host_context_cap_tokens || 0)}</strong><small>host ctx cap</small></span>
        <span><strong>${escapeHtml(providerReadiness.status || "not-configured")}</strong><small>provider readiness</small></span>
        <span><strong>${escapeHtml(providerReadiness.usable_provider_count || 0)}</strong><small>usable providers</small></span>
        <span><strong>${escapeHtml(developmentalReleaseContract.latest_status || "not-recorded")}</strong><small>developmental release contract</small></span>
        <span><strong>${escapeHtml(developmentalReleaseContract.canonical_output_count || 0)}</strong><small>canonical developmental outputs</small></span>
        <span><strong>${escapeHtml(firstRunReadiness.decision || "not-run")}</strong><small>first-run readiness</small></span>
        <span><strong>${escapeHtml(firstRunScope)}</strong><small>whole-system first-run scope</small></span>
        <span><strong>${escapeHtml(firstRunProduction.cycle_id || "none")}</strong><small>first-run production cycle</small></span>
        <span><strong>${escapeHtml(firstRunProduction.student_id || "none")}</strong><small>first-run student</small></span>
        <span><strong>${escapeHtml(latestProductionSpineReleaseLifecycle.status || productionSpineReleaseLifecycle.status || "not-run")}</strong><small>production-spine-release-lifecycle</small></span>
        <span><strong>${escapeHtml(productionSpineReleaseLifecycleApproval.status || "pending-admin-approval")}</strong><small>production spine lifecycle approval</small></span>
        <span><strong>${escapeHtml(productionSpineReleaseLifecycleGovernance.status || "missing")}</strong><small>production spine lifecycle governance</small></span>
        <span><strong>${escapeHtml(productionSpineReleaseLifecycleRollback.status || "not-rolled-back")}</strong><small>production spine lifecycle rollback</small></span>
        <span><strong>${escapeHtml(latestProductionSpineReleaseLifecycle.release_mutation_allowed ? "allowed" : "blocked")}</strong><small>production spine lifecycle mutation</small></span>
        <span><strong>${escapeHtml(releaseManifestRollup.status || "not_recorded")}</strong><small>release manifest rollup</small></span>
        <span><strong>${escapeHtml(releaseManifestRollup.release_mutation_allowed ? "allowed" : "blocked")}</strong><small>release mutation</small></span>
        <span><strong>${escapeHtml(releaseProductSmoke.latest_status || "not-run")}</strong><small>release product smoke</small></span>
        <span><strong>${escapeHtml(releaseRunHistory.latest_status || "not-run")}</strong><small>release run history</small></span>
        <span><strong>${escapeHtml(releaseRunHistory.run_count ?? 0)}</strong><small>release runs</small></span>
        <span><strong>${escapeHtml(canonContractLedger.coverage_status || "missing")}</strong><small>canon contract ledger</small></span>
        <span><strong>${escapeHtml(canonSourceManifest.ingested_source_count ?? 0)}/${escapeHtml(canonSourceManifest.source_count ?? 0)}</strong><small>canon sources</small></span>
        <span><strong>${escapeHtml(canonContractReceipts.receipt_count ?? 0)}</strong><small>canon receipts</small></span>
        <span><strong>${escapeHtml(canonContractReceipts.latest_status || "not-run")}</strong><small>latest canon receipt</small></span>
        <span><strong>${escapeHtml(releaseRuntime.update_boundary || "safe artifact only")}</strong><small>update boundary</small></span>
      </div>
    </article>
    ${renderUniversalEvolutionCard(evolution)}
    <article class="runtime-scorecard-card release-wrapper-canon-contract-ledger">
      <div class="metric-head">
        <strong>Canon contract ledger</strong>
        <span class="state-pill ${escapeHtml(canonContractLedger.coverage_status === "covered" ? "live-bound" : "shadow-only")}">${escapeHtml(pretty(canonContractLedger.coverage_status || "missing"))}</span>
      </div>
      <small>${escapeHtml(canonContractLedger.privacy_boundary || "sanitized-canon-source-refs-hashes-counts-headings-keyword-counts-and-runtime-evidence-refs-only-no-raw-canon-text-prompts-outputs-session-ids-or-local-paths")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(canonSourceManifest.ingested_source_count ?? 0)}</strong><small>ingested sources</small></span>
        <span><strong>${escapeHtml(canonSourceManifest.missing_source_count ?? 0)}</strong><small>missing sources</small></span>
        <span><strong>${escapeHtml(canonContractLedger.contract_count ?? 0)}</strong><small>contracts</small></span>
        <span><strong>${escapeHtml(canonContractLedger.evidence_present_count ?? 0)}</strong><small>evidence present</small></span>
        <span><strong>${escapeHtml(canonContractLedger.partial_count ?? 0)}</strong><small>partial contracts</small></span>
        <span><strong>${escapeHtml(canonContractLedger.active_production_mutation_allowed ? "allowed" : "blocked")}</strong><small>active mutation</small></span>
      </div>
      <div class="completion-scope">whole-project canon contract ledger | raw content ${escapeHtml(canonContractLedger.raw_content_included ? "included" : "redacted")} | source bytes ${escapeHtml(canonSourceManifest.total_byte_count ?? 0)}</div>
      ${scorecardLaneGrid((canonContractLedger.contracts || []).slice(0, 12).map((contract) => ({
        lane_id: contract.contract_id || "canon-contract",
        label: `${contract.label || "contract"} | ${(contract.blockers || [])[0] || contract.status || "unknown"}`,
        state: contract.status || "missing",
      })))}
      <div class="completion-scope">canon contract receipts | ${escapeHtml(canonContractReceipts.receipt_count ?? 0)} forward-pass receipts | latest ${escapeHtml(canonContractReceipts.latest_status || "not-run")}</div>
    </article>
    <article class="runtime-scorecard-card release-wrapper-forward-pass-enforcement-matrix">
      <div class="metric-head">
        <strong>Whole-system forward-pass matrix</strong>
        <span class="state-pill ${escapeHtml(forwardPassMatrix.coverage_status === "covered" ? "live-bound" : "shadow-only")}">${escapeHtml(pretty(forwardPassMatrix.coverage_status || "partial"))}</span>
      </div>
      <small>${escapeHtml(forwardPassMatrix.privacy_boundary || "sanitized-entrypoint-statuses-capability-columns-and-evidence-refs-only-no-prompts-outputs-session-ids-or-local-paths")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(forwardPassMatrix.covered_entrypoint_count || 0)}</strong><small>covered entrypoints</small></span>
        <span><strong>${escapeHtml(forwardPassMatrix.missing_entrypoint_count || 0)}</strong><small>missing entrypoints</small></span>
        <span><strong>${escapeHtml((forwardPassMatrix.required_capability_columns || []).length)}</strong><small>capability columns</small></span>
        <span><strong>${escapeHtml(forwardPassMatrix.active_production_mutation_allowed ? "allowed" : "blocked")}</strong><small>active mutation</small></span>
      </div>
      <div class="completion-scope">whole-system-forward-pass-enforcement-matrix | ${escapeHtml(forwardPassMatrix.go_no_go_blocking ? "go/no-go blocking" : "status-only non-blocking")} | raw content ${escapeHtml(forwardPassMatrix.raw_content_included ? "included" : "redacted")}</div>
      ${scorecardLaneGrid((forwardPassMatrix.entrypoints || []).slice(0, 12).map((row) => ({
        lane_id: row.entrypoint_id || "forward-pass-entrypoint",
        label: `${row.endpoint_ref || row.category || "entrypoint"} | ${row.blockers?.[0] || row.honest_status_label || row.status || "not-run"}`,
        state: row.status || "missing",
      })))}
    </article>
    <article class="runtime-scorecard-card release-wrapper-developmental-release-contract">
      <div class="metric-head">
        <strong>Developmental release contract</strong>
        <span class="state-pill ${escapeHtml(developmentalReleaseContract.runtime_state || "static-canon")}">${escapeHtml(pretty(developmentalReleaseContract.latest_status || "not-recorded"))}</span>
      </div>
      <small>${escapeHtml(developmentalReleaseContract.privacy_boundary || "canonical-developmental-ids-statuses-counts-and-digested-refs-only-no-prompts-outputs-session-ids-or-local-paths")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(developmentalReleaseContract.body_schema_snapshot?.surface_id || "not-recorded")}</strong><small>body schema snapshot</small></span>
        <span><strong>${escapeHtml((developmentalReleaseContract.reference_frame_updates || []).length)}</strong><small>reference frame updates</small></span>
        <span><strong>${escapeHtml(developmentalReleaseContract.dream_request?.status || "not-recorded")}</strong><small>dream request</small></span>
        <span><strong>${escapeHtml(developmentalReleaseContract.causal_test_request?.status || "not-recorded")}</strong><small>causal test request</small></span>
        <span><strong>${escapeHtml(developmentalReleaseContract.growth_archive_candidate?.promotion_state || "not-recorded")}</strong><small>growth archive candidate</small></span>
        <span><strong>${escapeHtml(developmentalReleaseContract.promotion_tribunal_case?.decision || "not-recorded")}</strong><small>promotion tribunal case</small></span>
      </div>
      <div class="completion-scope">developmental-release-contract | canonical outputs ${escapeHtml((developmentalReleaseContract.canonical_output_names || []).join(", ") || "not-recorded")} | production mutation ${escapeHtml(developmentalReleaseContract.active_production_mutation_allowed ? "allowed" : "blocked")}</div>
    </article>
    <article class="runtime-scorecard-card release-wrapper-boot-supervisor">
      <div class="metric-head">
        <strong>Release Harness boot supervisor</strong>
        <span class="state-pill ${escapeHtml(bootSupervisor.runtime_state || "not-run")}">${escapeHtml(pretty(bootSupervisor.latest_status || "not-run"))}</span>
      </div>
      <small>${escapeHtml(bootSupervisor.privacy_boundary || "sanitized-boot-refs-status-counts-digests-only-no-raw-prompts-outputs-session-ids")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(bootSupervisor.pass_count ?? 0)}</strong><small>checks pass</small></span>
        <span><strong>${escapeHtml(bootSupervisor.failed_count ?? 0)}</strong><small>checks blocked</small></span>
        <span><strong>${escapeHtml(bootSupervisor.evidence?.forward_pass_coverage?.latest_status || "not-run")}</strong><small>forward smoke</small></span>
        <span><strong>${escapeHtml(bootSupervisor.evidence?.release_readiness?.go_no_go || "no-go")}</strong><small>readiness gate</small></span>
        <span><strong>${escapeHtml(bootSupervisor.evidence?.release_readiness_evidence_runner?.latest_status || "not-run")}</strong><small>runner</small></span>
        <span><strong>${escapeHtml(bootProductPath.federated_packet_count ?? 0)}</strong><small>product-path federation</small></span>
        <span><strong>${escapeHtml(bootProductPath.dream_research_item_count ?? 0)}</strong><small>dream/research items</small></span>
        <span><strong>${escapeHtml(bootProductPath.self_repair_action_count ?? 0)}</strong><small>self repair actions</small></span>
        <span><strong>${escapeHtml(bootProductPathFailureLearning.latest_status || "not-run")}</strong><small>failure learning</small></span>
        <span><strong>${escapeHtml(bootSupervisor.manifest_ref || "artifacts/release-wrapper-runtime/boot-manifest.json")}</strong><small>manifest</small></span>
      </div>
      <div class="completion-scope">boot_supervisor | release-wrapper-boot-supervisor | release product path apply ${escapeHtml(bootProductPathAdmin.apply || "not-applied")} rollback ${escapeHtml(bootProductPathAdmin.rollback || "not-rolled-back")} | raw content ${escapeHtml(bootSupervisor.raw_content_included ? "included" : "redacted")}</div>
      <div class="surface-action-row">
        ${releaseWrapperActionButton("run_boot_supervisor", "Run Boot Supervisor", releaseActionLane.run_boot_supervisor_ref || state.releaseWrapperStatus?.endpoint_refs?.boot_supervisor_run || "/ops/wrapper/boot-supervisor/run")}
        ${releaseWrapperActionButton("run_initial_release_supervisor", "Run Initial Release Supervisor", releaseActionLane.run_initial_release_supervisor_ref || state.releaseWrapperStatus?.endpoint_refs?.initial_release_supervisor_run || "/ops/wrapper/initial-release-supervisor/run")}
        ${releaseWrapperActionButton("run_release_product_smoke", "Run Product Smoke", releaseActionLane.run_release_product_smoke_ref || state.releaseWrapperStatus?.endpoint_refs?.release_product_smoke_run || "/ops/wrapper/release-product-smoke/run")}
        ${releaseWrapperActionButton("run_release_health_heartbeat_loop", "Run Health Loop", releaseActionLane.run_release_health_heartbeat_loop_ref || state.releaseWrapperStatus?.endpoint_refs?.release_health_heartbeat_loop_run || "/ops/wrapper/release-health-heartbeat/run")}
      </div>
      ${scorecardLaneGrid((bootSupervisor.checks || []).slice(0, 6).map((check) => ({
        lane_id: check.check_id || "release-wrapper-boot-supervisor",
        label: `${check.endpoint || "endpoint"} | raw ${check.raw_content_included ? "included" : "redacted"}`,
        state: check.status || "not-run",
      })))}
    </article>
    <article class="runtime-scorecard-card release-wrapper-operation-receipts">
      <div class="metric-head">
        <strong>Release Harness operation receipts</strong>
        <span class="state-pill ${operationReceiptRows.length && operationReceiptRows.length === coveredOperationReceiptRows.length ? "live-bound" : "shadow-only"}">${escapeHtml(pretty(operationReceiptRows.length ? `${coveredOperationReceiptRows.length}/${operationReceiptRows.length} covered` : "not-recorded"))}</span>
      </div>
      <small>Runtime receipts for federated import, admin approval, sandbox, safe apply, and rollback; diagnostic only and not a readiness authority.</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(operationReceiptRefs.length)}</strong><small>operation receipt refs</small></span>
        <span><strong>${escapeHtml(latestFederatedImportReceipt.status || "not-imported")}</strong><small>federated import receipt</small></span>
        <span><strong>${escapeHtml(selfRepairOperationReceiptActions.length)}</strong><small>self-repair operation receipt count</small></span>
        <span><strong>${escapeHtml(latestSelfRepairOperationReceipt.status || "not-recorded")}</strong><small>latest self-repair operation receipt</small></span>
        <span><strong>${escapeHtml(latestFederatedImportReceipt.raw_content_included ? "included" : "redacted")}</strong><small>import raw content</small></span>
        <span><strong>${escapeHtml(latestSelfRepairOperationReceipt.active_production_mutated ? "mutated" : "unchanged")}</strong><small>active production</small></span>
      </div>
      <div class="completion-scope">operation receipt refs | ${escapeHtml(operationReceiptRefs.join(", ") || "none")} | raw content redacted | active production mutation blocked</div>
      ${scorecardLaneGrid(operationReceiptRows.slice(0, 6).map((row) => ({
        lane_id: row.entrypoint_id || row.operation_receipt?.receipt_id || "operation-receipt",
        label: `${row.entrypoint_id || "entrypoint"} | receipt ${row.operation_receipt?.status || "missing"} | ${row.operation_receipt?.receipt_id || "no-receipt"}`,
        state: row.operation_receipt?.status === "covered" ? "live-bound" : "blocked",
      })))}
    </article>
    <article class="runtime-scorecard-card release-wrapper-release-product-smoke">
      <div class="metric-head">
        <strong>Release product smoke</strong>
        <span class="state-pill ${escapeHtml(releaseProductSmoke.runtime_state || "not-run")}">${escapeHtml(pretty(releaseProductSmoke.latest_status || "not-run"))}</span>
      </div>
      <small>${escapeHtml(releaseProductSmoke.privacy_boundary || "sanitized-release-product-smoke-status-counts-digests-and-endpoint-refs-only-no-prompts-outputs-session-ids-or-local-paths")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(releaseProductSmoke.pass_count ?? 0)}</strong><small>checks pass</small></span>
        <span><strong>${escapeHtml(releaseProductSmoke.failed_count ?? 0)}</strong><small>checks blocked</small></span>
        <span><strong>${escapeHtml(releaseProductSmoke.evidence?.release_readiness?.go_no_go || "no-go")}</strong><small>readiness gate</small></span>
        <span><strong>${escapeHtml(releaseProductSmoke.evidence?.control_panel?.matrix_coverage_status || "partial")}</strong><small>control panel matrix</small></span>
        <span><strong>${escapeHtml(releaseProductSmoke.manifest_ref || "artifacts/release-wrapper-runtime/release-product-smoke.json")}</strong><small>manifest</small></span>
      </div>
      <div class="surface-action-row">
        ${releaseWrapperActionButton("run_release_product_smoke", "Run Product Smoke", releaseActionLane.run_release_product_smoke_ref || state.releaseWrapperStatus?.endpoint_refs?.release_product_smoke_run || "/ops/wrapper/release-product-smoke/run")}
      </div>
      <div class="completion-scope">release product smoke | ${escapeHtml(releaseProductSmoke.product_scope || "whole-system")} | raw content ${escapeHtml(releaseProductSmoke.raw_content_included ? "included" : "redacted")} | active mutation ${escapeHtml(releaseProductSmoke.active_production_mutated ? "mutated" : "blocked")}</div>
      ${scorecardLaneGrid((releaseProductSmoke.checks || []).slice(0, 7).map((check) => ({
        lane_id: check.check_id || "release-product-smoke",
        label: `${check.endpoint || "endpoint"} | raw ${check.raw_content_included ? "included" : "redacted"}`,
        state: check.status || "not-run",
      })))}
    </article>
    <article class="runtime-scorecard-card release-wrapper-release-run-history">
      <div class="metric-head">
        <strong>Release run history</strong>
        <span class="state-pill ${escapeHtml(releaseRunHistory.runtime_state || "not-run")}">${escapeHtml(pretty(releaseRunHistory.latest_status || "not-run"))}</span>
      </div>
      <small>${escapeHtml(releaseRunHistory.privacy_boundary || "sanitized-release-run-history-status-counts-digests-and-endpoint-refs-only-no-prompts-outputs-admin-identities-session-ids-or-local-paths")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(releaseRunHistory.run_count ?? 0)}</strong><small>session runs</small></span>
        <span><strong>${escapeHtml(releaseRunHistory.global_run_count ?? 0)}</strong><small>global runs</small></span>
        <span><strong>${escapeHtml(releaseRunHistory.latest_run?.run_kind || "not-run")}</strong><small>latest kind</small></span>
        <span><strong>${escapeHtml(releaseRunHistory.latest_run?.run_sequence ?? 0)}</strong><small>latest sequence</small></span>
        <span><strong>${escapeHtml(releaseRunHistory.manifest_ref || "artifacts/release-wrapper-runtime/release-run-history.jsonl")}</strong><small>history artifact</small></span>
      </div>
      <div class="completion-scope">release run history | ${escapeHtml(releaseRunHistory.product_scope || "whole-system")} | raw content ${escapeHtml(releaseRunHistory.raw_content_included ? "included" : "redacted")} | active mutation ${escapeHtml(releaseRunHistory.active_production_mutation_allowed ? "allowed" : "blocked")}</div>
      ${scorecardLaneGrid((releaseRunHistory.runs || []).slice(-6).map((run) => ({
        lane_id: run.run_id || "release-run",
        label: `${run.run_kind || "release-run"} | ${run.product_scope || "whole-system"} | checks ${run.pass_count ?? 0}/${run.check_count ?? 0}`,
        state: run.status || "not-run",
      })))}
    </article>
    <article class="runtime-scorecard-card release-wrapper-live-telemetry">
      <div class="metric-head">
        <strong>Release Harness live telemetry</strong>
        <span class="state-pill ${escapeHtml(releaseTelemetry.runtime_state || "static-canon")}">${escapeHtml(pretty(releaseTelemetry.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(releaseTelemetry.privacy_boundary || "sanitized-digests-refs-counts-and-status-only-no-raw-prompts-outputs-session-ids")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(releaseTelemetry.event_count || 0)}</strong><small>runtime events</small></span>
        <span><strong>${escapeHtml(telemetryAssimilation.capture_count || 0)}</strong><small>assimilation captures</small></span>
        <span><strong>${escapeHtml(telemetryGrowth.global_captures || 0)}</strong><small>growth captures</small></span>
        <span><strong>${escapeHtml(telemetryFailureLearning.captured_count || 0)}</strong><small>failure learning captures</small></span>
        <span><strong>${escapeHtml(telemetryFederation.packet_count || 0)}</strong><small>federated packets</small></span>
        <span><strong>${escapeHtml(telemetryProduction.packet_count || 0)}</strong><small>production spine packets</small></span>
      </div>
      <div class="completion-scope release-wrapper-failure-learning">live_wrapper_telemetry source ${escapeHtml(releaseTelemetry.source || "release-wrapper-runtime-events")} | recent_events ${escapeHtml(String(telemetryEvents.length))} | failure learning ${escapeHtml(telemetryFailureLearning.latest_status || "not-run")}</div>
      ${scorecardLaneGrid(telemetryEvents.slice(0, 4).map((event) => ({
        lane_id: event.trace_id || event.federated_packet_id || "wrapper-event",
        label: `${event.expert_node || "expert"} | packet ${event.federated_packet_id || "none"} | failure ${event.failure_learning_signal_status || "none"} | raw ${event.raw_content_included ? "included" : "redacted"}`,
        state: event.raw_content_included ? "blocked" : "live-bound",
      })))}
    </article>
    <article class="runtime-scorecard-card release-harness-cluster9-teacher-reconciliation">
      <div class="metric-head">
        <strong>Cluster 9 teacher reconciliation</strong>
        <span class="state-pill ${cluster9TeacherReconciliation.birth_blocking_issue_count ? "blocked" : "shadow-only"}">${escapeHtml(cluster9TeacherReconciliation.birth_blocking_issue_count ? "blocked" : "paired")}</span>
      </div>
      <small>${escapeHtml(cluster9TeacherReconciliation.autonomy_rule || "birth, merge, split, retire, and live-problem temporary experts require eval evidence, rollback, and NexusBrain approval")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(cluster9TeacherReconciliation.node_count || 0)}</strong><small>role nodes</small></span>
        <span><strong>${escapeHtml(cluster9TeacherReconciliation.node_type_counts?.orchestrator || 0)}</strong><small>orchestrators</small></span>
        <span><strong>${escapeHtml(cluster9TeacherReconciliation.node_type_counts?.assistant_orchestrator || 0)}</strong><small>AOs</small></span>
        <span><strong>${escapeHtml(cluster9TeacherReconciliation.node_type_counts?.expert || 0)}</strong><small>experts</small></span>
        <span><strong>${escapeHtml(cluster9TeacherReconciliation.node_type_counts?.temporary_expert || 0)}</strong><small>temporary experts</small></span>
        <span><strong>${escapeHtml(cluster9TeacherReconciliation.pairing_gap_count || 0)}</strong><small>pairing gaps</small></span>
        <span><strong>${escapeHtml(cluster9TeacherReconciliation.birth_blocking_issue_count || 0)}</strong><small>birth blockers</small></span>
        <span><strong>${escapeHtml(cluster9TeacherReconciliation.live_problem_temporary_experts?.shadow_only ? "shadow-only" : "blocked")}</strong><small>live-problem experts</small></span>
      </div>
      <div class="completion-scope">cluster9_teacher_reconciliation | ${escapeHtml(cluster9TeacherReconciliation.mother_brain_authority || "NexusBrain")} owns hive authority | raw content ${escapeHtml(cluster9TeacherReconciliation.raw_content_included ? "included" : "redacted")} | active mutation ${escapeHtml(cluster9TeacherReconciliation.active_production_mutation_allowed ? "allowed" : "blocked")}</div>
    </article>
    <article class="runtime-scorecard-card release-wrapper-session-lifecycle">
      <div class="metric-head">
        <strong>Release Harness session lifecycle</strong>
        <span class="state-pill ${releaseLifecycle.readiness?.go_no_go === "go" ? "live-bound" : "shadow-only"}">${escapeHtml(pretty(releaseLifecycle.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(releaseLifecycle.privacy_boundary || "sanitized-session-lifecycle-digests-refs-status-only-no-raw-prompts-outputs-session-ids")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(lifecycleStepCounts.passed ?? 0)}</strong><small>steps pass</small></span>
        <span><strong>${escapeHtml(lifecycleStepCounts.blocked ?? 0)}</strong><small>steps blocked</small></span>
        <span><strong>${escapeHtml(sessionHistory.event_count ?? 0)}</strong><small>session history</small></span>
        <span><strong>${escapeHtml(sessionHistory.global_event_count ?? 0)}</strong><small>global history</small></span>
        <span><strong>${escapeHtml(releaseLifecycle.readiness?.go_no_go || "no-go")}</strong><small>release gate</small></span>
        <span><strong>${escapeHtml(releaseManifestLifecycleStep.status || releaseManifestRollup.status || "not_recorded")}</strong><small>release-manifest-rollup</small></span>
        <span><strong>${escapeHtml(releaseManifestMutationLabel)}</strong><small>release manifest mutation boundary</small></span>
        <span><strong>${escapeHtml(releaseManifestRollup.control_panel_label || "Release manifest status not recorded")}</strong><small>release manifest operator label</small></span>
        <span><strong>${escapeHtml(releaseLifecycle.session_lifecycle_ref || "/ops/wrapper/session-lifecycle")}</strong><small>lifecycle</small></span>
      </div>
      <div class="completion-scope">releaseWrapperSessionLifecycle | session_history ${escapeHtml(sessionHistory.surface_id || "release-wrapper-session-history")} | ${escapeHtml(releaseLifecycle.autonomous_update_path?.update_boundary || "admin-approved-shadow-eval-sandbox-safe-file-apply-rollback-only")}</div>
      ${scorecardLaneGrid(visibleLifecycleSteps.map((step) => ({
        lane_id: step.step_id || "release-wrapper-session-lifecycle",
        label: `${step.order || "?"}. ${step.label || "lifecycle step"}${step.step_id === "release-manifest-rollup" ? ` | ${releaseManifestMutationLabel}` : ""}`,
        state: step.status || "blocked",
      })))}
    </article>
    <article class="runtime-scorecard-card release-wrapper-self-repair-ledger">
      <div class="metric-head">
        <strong>Release Harness self repair ledger</strong>
        <span class="state-pill ${selfRepairLedger.repair_count ? "live-bound" : "shadow-only"}">${escapeHtml(pretty(selfRepairLedger.latest_status || "not-run"))}</span>
      </div>
      <small>${escapeHtml(selfRepairLedger.privacy_boundary || "sanitized-update-session-digests-and-evidence-refs-only-no-raw-prompts-outputs-session-ids")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(selfRepairLedger.repair_count ?? 0)}</strong><small>session repairs</small></span>
        <span><strong>${escapeHtml(selfRepairLedger.global_repair_count ?? 0)}</strong><small>global repairs</small></span>
        <span><strong>${escapeHtml(selfRepairLedger.ao_guard_passed_count ?? 0)}</strong><small>AO guarded actions</small></span>
        <span><strong>${escapeHtml(selfRepairLedger.authority_decision_count ?? 0)}</strong><small>authority effect receipts</small></span>
        <span><strong>${escapeHtml(latestSelfRepairGuard.passed ? "passed" : "not-run")}</strong><small>latest AO guard</small></span>
        <span><strong>${escapeHtml(latestSelfRepairGuardReceipts.length)}</strong><small>guard receipts</small></span>
        <span><strong>${escapeHtml(selfRepairLedger.latest_action || "none")}</strong><small>latest action</small></span>
        <span><strong>${escapeHtml(selfRepairLedger.latest_status || "not-run")}</strong><small>latest status</small></span>
      </div>
      <div class="completion-scope">self_repair_ledger ${escapeHtml(selfRepairLedger.surface_id || "release-wrapper-self-repair-ledger")} | AO guard receipts ${escapeHtml(selfRepairLedger.ao_guard_passed_count ?? 0)} | authority effect receipts ${escapeHtml(selfRepairLedger.authority_decision_count ?? 0)} | ${escapeHtml(selfRepairLedger.mutation_boundary || "admin-approved-shadow-safe-file-only-no-active-production-mutation")}</div>
      ${scorecardLaneGrid((selfRepairLedger.actions || []).slice(-4).map((action) => ({
        lane_id: action.repair_run_id || action.action || "self-repair-action",
        label: `${action.action || "action"} | ${action.status || "recorded"} | guard ${action.ao_guard?.passed ? "passed" : "missing"} | self-repair operation receipt ${action.operation_receipt?.status || "missing"} | active ${action.active_production_mutated ? "mutated" : "unchanged"}`,
        state: action.active_production_mutated || action.operation_receipt?.status === "degraded" ? "blocked" : action.operation_receipt?.status === "covered" ? "live-bound" : "shadow-only",
      })))}
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Release readiness</strong>
        <span class="state-pill ${releaseReadiness.go_no_go === "go" ? "live-bound" : "blocked"}">${escapeHtml(pretty(releaseReadiness.go_no_go || "no-go"))}</span>
      </div>
      <small>${escapeHtml(releaseReadiness.artifact_path || "release readiness manifest not persisted")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(passedReadiness)}</strong><small>passed checks</small></span>
        <span><strong>${escapeHtml(blockedReadiness)}</strong><small>blocked checks</small></span>
        <span><strong>${escapeHtml((releaseReadiness.blockers || []).length)}</strong><small>blockers</small></span>
        <span><strong>${escapeHtml(releaseReadiness.boot?.readiness_ref || "/ops/wrapper/release-readiness")}</strong><small>manifest</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.promotion_boundary || "autonomous updates require gated shadow promotion")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.proposal_count || 0)}</strong><small>proposals</small></span>
        <span><strong>${escapeHtml(scorecard.shadow_ready_count || 0)}</strong><small>shadow</small></span>
        <span><strong>${escapeHtml(scorecard.blocked_count || 0)}</strong><small>blocked</small></span>
        <span><strong>${escapeHtml(scorecard.sandbox_test_evidence_count || 0)}</strong><small>test evidence</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(latest.update_id || scorecard.self_improvement_boundary || "No autonomous update proposals recorded")}</div>
    <article class="runtime-scorecard-card release-wrapper-admin-action-lane">
      <div class="metric-head">
        <strong>Release Harness admin lane</strong>
        <span class="state-pill ${releaseActionStatuses.apply === "applied-shadow-safe-file" ? "live-bound" : "shadow-only"}">${escapeHtml(pretty(releaseActionStatuses.proposal || "not-generated"))}</span>
      </div>
      <small>${escapeHtml(releaseActionLane.proposal_update_id || "No release Harness proposal available")}</small>
      <div class="surface-action-row">
        ${releaseWrapperActionButton("admin_approval", "Approve", releaseActionLane.admin_approval_ref)}
        ${releaseWrapperActionButton("sandbox_tests", "Sandbox", releaseActionLane.sandbox_tests_ref)}
        ${releaseWrapperActionButton("apply", "Apply", releaseActionLane.apply_ref)}
        ${releaseWrapperActionButton("rollback", "Rollback", releaseActionLane.rollback_ref)}
        ${releaseWrapperActionButton("run_release_readiness_evidence", "Run readiness evidence", releaseActionLane.run_readiness_evidence_ref)}
        ${releaseWrapperActionButton("run_release_product_smoke", "Run Product Smoke", releaseActionLane.run_release_product_smoke_ref)}
        ${releaseWrapperActionButton("run_release_health_heartbeat_loop", "Run Health Loop", releaseActionLane.run_release_health_heartbeat_loop_ref)}
        ${releaseWrapperActionButton("configure_release_health_heartbeat_supervisor", "Configure Health Supervisor", releaseActionLane.configure_release_health_heartbeat_supervisor_ref)}
        ${releaseWrapperActionButton("run_release_health_heartbeat_supervisor_repair", "Run Health Repair", releaseActionLane.run_release_health_heartbeat_supervisor_repair_ref)}
        ${releaseWrapperActionButton("refresh_status_card", "Refresh", releaseActionLane.status_card_ref || "/ops/wrapper/status-card")}
      </div>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(releaseActionStatuses.admin_approval || "pending-admin-approval")}</strong><small>approval</small></span>
        <span><strong>${escapeHtml(releaseActionStatuses.sandbox_tests || "not-run")}</strong><small>sandbox</small></span>
        <span><strong>${escapeHtml(releaseActionStatuses.apply || "not-applied")}</strong><small>apply</small></span>
        <span><strong>${escapeHtml(releaseActionStatuses.rollback || "not-rolled-back")}</strong><small>rollback</small></span>
        <span><strong>${escapeHtml(releaseActionStatuses.readiness_runner || "not-run")}</strong><small>runner</small></span>
        <span><strong>${escapeHtml(releaseActionStatuses.release_product_smoke || releaseProductSmoke.latest_status || "not-run")}</strong><small>product smoke</small></span>
        <span><strong>${escapeHtml(releaseActionStatuses.release_health_heartbeat_loop || releaseHealthHeartbeatLoop.status || "not-run")}</strong><small>release health loop</small></span>
        <span><strong>${escapeHtml(releaseActionStatuses.release_health_heartbeat_supervisor || releaseHealthHeartbeatSupervisor.status || "disabled")}</strong><small>release health supervisor</small></span>
        <span><strong>${escapeHtml(releaseActionStatuses.release_health_heartbeat_supervisor_repair || "not-run")}</strong><small>health repair</small></span>
      </div>
      <div class="completion-scope">${escapeHtml(releaseActionLane.default_sandbox_command || "pytest tests/test_release_wrapper_runtime.py::test_release_wrapper_status_card_is_lightweight_control_panel_surface_after_restart -q")}</div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Sandbox test evidence</strong>
        <span class="state-pill ${latestSandbox.passed ? "live-bound" : "static-canon"}">${escapeHtml(latestSandbox.status || "not-run")}</span>
      </div>
      <small>${escapeHtml(latestSandbox.evidence_ref || "safe apply requires persisted sandbox evidence")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(latestSandbox.sandbox?.shell_used ? "shell" : "no shell")}</strong><small>executor</small></span>
        <span><strong>${escapeHtml(latestSandbox.returncode ?? "n/a")}</strong><small>return</small></span>
        <span><strong>${escapeHtml(latestSandbox.failure_count ?? 0)}</strong><small>failures</small></span>
        <span><strong>${escapeHtml(sandboxModeLabel)}</strong><small>mode</small></span>
        <span><strong>${escapeHtml(sandboxDiff.unsafe_change_count ?? 0)}</strong><small>unsafe_change_count</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Autonomous upstream eval gate</strong>
        <span class="state-pill ${upstream_eval_gate.promotion_allowed === false ? "blocked" : "live-bound"}">${upstream_eval_gate.promotion_allowed === false ? "blocked" : "clear"}</span>
      </div>
      <small>${escapeHtml(upstream_eval_gate.source || "upstream eval gate")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(upstream_eval_gate.promotion_allowed === false ? "blocked" : "clear")}</strong><small>upstream eval gate</small></span>
        <span><strong>${escapeHtml(upstream_lifecycle_gate.lifecycle_status || "unknown")}</strong><small>lifecycle</small></span>
        <span><strong>${escapeHtml(upstream_lifecycle_gate.growth_engine_gate_allowed === false ? "blocked" : "clear")}</strong><small>growth</small></span>
        <span><strong>${escapeHtml(upstream_eval_gate.blockers?.length || 0)}</strong><small>blockers</small></span>
      </div>
    </article>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Shadow eval replay evidence</strong>
        <span class="state-pill ${latestEvalReplay.status === "passed-shadow" ? "live-bound" : "static-canon"}">${escapeHtml(latestEvalReplay.status || "not-run")}</span>
      </div>
      <small>${escapeHtml(latestEvalReplay.run_id || "latest_eval_replay not recorded for latest proposal")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(latestEvalReplay.promotion_allowed ? "allowed" : "pending")}</strong><small>promotion</small></span>
        <span><strong>${escapeHtml(latestEvalReplay.operator_approved ? "approved" : "not approved")}</strong><small>operator</small></span>
        <span><strong>${escapeHtml(latestEvalReplay.suite_id || "none")}</strong><small>suite</small></span>
        <span><strong>${escapeHtml(latestEvalReplay.evidence_refs?.length || 0)}</strong><small>evidence refs</small></span>
      </div>
    </article>
    ${scorecardLaneGrid(proposals.slice(0, 6).map((proposal) => ({
      lane_id: proposal.update_id,
      label: `${proposal.update_type || "update"} | ${proposal.requested_state || "proposal"} | ${proposal.promotion_state || "gate"}`,
      state: proposal.status || "static-canon",
    })))}
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderReleaseWrapperStatusFallback(statusCard, sessionLifecycle) {
  if (!statusCard) {
    return;
  }
  state.releaseWrapperStatus = statusCard;
  state.autonomousUpdates = statusCard.autonomous_updates || state.autonomousUpdates;
  state.releaseWrapperRuntime = statusCard.runtime || state.releaseWrapperRuntime;
  state.releaseHarnessRuntime = statusCard.runtime || state.releaseHarnessRuntime;
  state.cluster9TeacherReconciliation = statusCard.cluster9_teacher_reconciliation
    || statusCard.runtime?.cluster9_teacher_reconciliation
    || state.cluster9TeacherReconciliation;
  state.releaseWrapperTelemetry = statusCard.runtime?.live_wrapper_telemetry || state.releaseWrapperTelemetry;
  state.releaseWrapperReadiness = statusCard.readiness || state.releaseWrapperReadiness;
  if (sessionLifecycle) {
    state.releaseWrapperSessionLifecycle = sessionLifecycle;
  }
  const runtime = state.releaseWrapperRuntime || {};
  const matrix = runtime.whole_system_forward_pass_enforcement_matrix || statusCard.whole_system_forward_pass_enforcement_matrix || {};
  const nativeHiveHeartbeatWatchdog = runtime.native_hive_heartbeat_watchdog || statusCard.native_hive_heartbeat_watchdog || {};
  const releaseHealthHeartbeat = runtime.release_health_heartbeat || statusCard.release_health_heartbeat || {};
  const releaseHealthHeartbeatLoop = runtime.release_health_heartbeat_loop || statusCard.release_health_heartbeat_loop || {};
  const releaseHealthHeartbeatSupervisor = runtime.release_health_heartbeat_supervisor
    || statusCard.release_health_heartbeat_supervisor
    || {};
  const receiptRows = (matrix.entrypoints || []).filter((row) => row.operation_receipt?.receipt_id);
  const coveredReceiptRows = receiptRows.filter((row) => row.operation_receipt?.status === "covered");
  const inboxReceipt = runtime.federated_packet_inbox?.latest_import?.operation_receipt || {};
  const selfRepairActions = (runtime.self_repair_ledger?.actions || []).filter((action) => action.operation_receipt?.receipt_id);
  fill(dom.runtimeScorecard, `
    <article class="runtime-scorecard-card release-wrapper-status-card-fallback">
      <div class="metric-head">
        <strong>Release Harness status-card fallback</strong>
        <span class="state-pill shadow-only">Loading full visualizer state</span>
      </div>
      <small>Lightweight Harness status rendered before the read-only visualizer overlay finishes loading.</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(matrix.coverage_status || "partial")}</strong><small>forward-pass matrix</small></span>
        <span><strong>${escapeHtml(`${coveredReceiptRows.length}/${receiptRows.length}`)}</strong><small>operation receipt refs</small></span>
        <span><strong>${escapeHtml(inboxReceipt.status || "not-imported")}</strong><small>federated import receipt</small></span>
        <span><strong>${escapeHtml(selfRepairActions.length)}</strong><small>self-repair operation receipt</small></span>
        <span><strong>${escapeHtml(nativeHiveHeartbeatWatchdog.status || "blocked")}</strong><small>Heartbeat watchdog</small></span>
        <span><strong>${escapeHtml(releaseHealthHeartbeat.status || "not-run")}</strong><small>Release health heartbeat</small></span>
        <span><strong>${escapeHtml(releaseHealthHeartbeatLoop.status || "not-run")}</strong><small>Release health loop</small></span>
        <span><strong>${escapeHtml(releaseHealthHeartbeatSupervisor.status || "disabled")}</strong><small>Release heartbeat supervisor</small></span>
        <span><strong>${escapeHtml(statusCard.readiness?.go_no_go || "no-go")}</strong><small>release gate</small></span>
      </div>
      <div class="completion-scope">release-wrapper-status-card-fallback | diagnostic status only | raw content redacted | active production mutation blocked</div>
    </article>
  `);
  renderAutonomousUpdatesScorecard();
  setConnection("shadow-only", "Loading full visualizer state | Harness status-card fallback rendered");
}

function renderBlackBoxRecorder() {
  const recorder = state.blackBox || {};
  const frames = recorder.frames || [];
  fill(dom.blackBoxRecorder, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(recorder.authority || "NexusBrain")}</strong>
        <span class="state-pill ${recorder.active_command_id ? "live-bound" : "static-canon"}">${escapeHtml(recorder.active_command_id ? "recording" : "standby")}</span>
      </div>
      <small>${escapeHtml(recorder.active_command_id || "No active command in this session")}</small>
      <div class="token-grid">${(recorder.export_contract?.standard_mappings || []).map((item) => `<span class="token">${escapeHtml(item)}</span>`).join("")}</div>
    </article>
    ${scorecardLaneGrid(frames, "frame_id")}
    <div class="completion-scope">${escapeHtml(recorder.export_contract?.proof_rule || "every operator claim carries evidence")}</div>
  `);
}

function renderHiveConsensusScorecard() {
  const scorecard = state.hiveConsensus || {};
  const frames = scorecard.signal_frames || [];
  const chain = scorecard.command_chain || [];
  fill(dom.hiveConsensusScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${scorecard.active_command_id ? "live-bound" : "static-canon"}">${escapeHtml(scorecard.lifecycle_state || "standby")}</span>
      </div>
      <small>${escapeHtml(chain.join(" -> ") || "NexusBrain -> AO Hive -> Experts -> Tools -> Memory -> NexusBrain")}</small>
      <div class="token-grid">${(scorecard.signal_contract || []).map((item) => `<span class="token">${escapeHtml(signalLabel(item))}</span>`).join("")}</div>
    </article>
    ${scorecardLaneGrid(scorecard.consensus_rules || [], "rule_id")}
    ${scorecardLaneGrid(frames, "frame_id")}
  `);
}

function renderAoHiveScorecard() {
  const scorecard = state.aoHive || {};
  const roster = scorecard.ao_roster || [];
  fill(dom.aoHiveScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${scorecard.active_command_id ? "live-bound" : "static-canon"}">${escapeHtml(scorecard.delegation_model?.selected_ao || "standby")}</span>
      </div>
      <small>${escapeHtml(scorecard.delegation_model?.delegation_rule || "AOs report to NexusBrain")}</small>
      <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
    </article>
    <div class="scorecard-mini-grid">
      ${roster.map((ao) => `
        <article class="runtime-scorecard-card">
          <div class="metric-head">
            <strong>${escapeHtml(ao.ao_name || "AO")}</strong>
            <span class="state-pill ${escapeHtml(ao.risk_tier === "high" ? "shadow-only" : "live-bound")}">${escapeHtml(ao.risk_tier || "medium")}</span>
          </div>
          <small>${escapeHtml(ao.context_scope || ao.description || "")}</small>
          <div class="token-grid">${(ao.model_tool_permissions || []).slice(0, 4).map((item) => `<span class="token">${escapeHtml(item)}</span>`).join("")}</div>
        </article>
      `).join("")}
    </div>
  `);
}

function renderExpertsHiveScorecard() {
  const scorecard = state.expertsHive || {};
  const experts = scorecard.domain_experts || [];
  fill(dom.expertsHiveScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${scorecard.active_command_id ? "live-bound" : "static-canon"}">${escapeHtml(scorecard.routing_model?.selected_expert || "standby")}</span>
      </div>
      <small>${escapeHtml(scorecard.mini_brain_model?.topology_rule || "each expert is a mini NexusNet under NexusBrain authority")}</small>
      <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
    </article>
    <div class="scorecard-mini-grid">
      ${experts.map((expert) => `
        <article class="runtime-scorecard-card">
          <div class="metric-head">
            <strong>${escapeHtml(expert.display_name || expert.subject || "Expert")}</strong>
            <span class="state-pill ${escapeHtml(expert.consensus_state === "selected-route" ? "live-bound" : "static-canon")}">${escapeHtml(pretty(expert.consensus_state || "available"))}</span>
          </div>
          <small>${escapeHtml(expert.role_hint || "")}</small>
          <div class="token-grid">${(expert.model_tool_permissions || []).slice(0, 4).map((item) => `<span class="token">${escapeHtml(item)}</span>`).join("")}</div>
        </article>
      `).join("")}
    </div>
  `);
}

function renderResearcherSwarmScorecard() {
  const scorecard = state.researcherSwarm || {};
  const roles = scorecard.research_roles || [];
  const stages = scorecard.promotion_loop || [];
  fill(dom.researcherSwarmScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.active_research_watch?.answer_state || "static-canon")}">${escapeHtml(pretty(scorecard.active_research_watch?.answer_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.autonomy_rule || "research proposes; NexusBrain and operator approve")}</small>
      <div class="token-grid">${(scorecard.candidate_registry || []).slice(0, 8).map((item) => `<span class="token">${escapeHtml(item.label || item.lane_id || "candidate")}</span>`).join("")}</div>
    </article>
    ${scorecardLaneGrid(roles, "role_id")}
    ${scorecardLaneGrid(stages, "stage_id")}
  `);
}

function renderForwardRadarScorecard() {
  const scorecard = state.forwardRadar || {};
  const latest = scorecard.latest_candidate || {};
  const upstream_harness_ledger_gate = latest.upstream_harness_ledger_gate || {};
  const upstream_self_review_gate = upstream_harness_ledger_gate.upstream_self_review_gate || {};
  const upstream_eval_gate = upstream_self_review_gate.upstream_eval_gate || {};
  const harness_gate_blocked = upstream_harness_ledger_gate.promotion_allowed === false || upstream_harness_ledger_gate.status === "blocked";
  const candidates = scorecard.candidates || [];
  fill(dom.forwardRadarScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.autonomy_rule || "discover and propose, but gate before promotion")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.candidate_count || 0)}</strong><small>candidates</small></span>
        <span><strong>${escapeHtml(scorecard.promotion_ready_count || 0)}</strong><small>ready</small></span>
        <span><strong>${escapeHtml(scorecard.watchlist_count || 0)}</strong><small>watch</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(latest.title || "No live Forward Radar reviews recorded")}</div>
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Forward Radar upstream harness-ledger gate</strong>
        <span class="state-pill ${harness_gate_blocked ? "blocked" : "live-bound"}">${harness_gate_blocked ? "blocked" : "clear"}</span>
      </div>
      <small>${escapeHtml(upstream_harness_ledger_gate.source || "upstream harness-ledger gate")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(upstream_harness_ledger_gate.promotion_allowed === false ? "blocked" : "clear")}</strong><small>harness</small></span>
        <span><strong>${escapeHtml(upstream_self_review_gate.review_state || upstream_self_review_gate.status || "unknown")}</strong><small>self-review</small></span>
        <span><strong>${escapeHtml(upstream_eval_gate.promotion_allowed === false ? "blocked" : "clear")}</strong><small>upstream eval</small></span>
        <span><strong>${escapeHtml(upstream_harness_ledger_gate.blockers?.length || 0)}</strong><small>blockers</small></span>
      </div>
    </article>
    ${scorecardLaneGrid(candidates.slice(0, 6).map((candidate) => ({
      lane_id: candidate.radar_id,
      label: `${candidate.lane || "lane"} | ${candidate.gate_summary?.passed_gate_count || 0}/8 gates | ${candidate.title || "candidate"}`,
      state: candidate.status || "research-candidate",
    })))}
    <div class="token-grid">${(scorecard.required_gates || []).map((gate) => `<span class="token">${escapeHtml(pretty(gate))}</span>`).join("")}</div>
  `);
}

function renderEvalSuiteScorecard() {
  const scorecard = state.evalSuite || {};
  const evals = scorecard.eval_families || [];
  fill(dom.evalSuiteScorecard, `
    <div class="scorecard-mini-grid">
      ${evals.map((item) => `
        <article class="runtime-scorecard-card">
          <div class="metric-head">
            <strong>${escapeHtml(item.eval_id)}</strong>
            <span class="state-pill ${escapeHtml(item.state || "research-candidate")}">${escapeHtml(pretty(item.state || "research-candidate"))}</span>
          </div>
          <small>${escapeHtml(item.label || "")}</small>
        </article>
      `).join("")}
    </div>
    <div class="token-grid">${(scorecard.promotion_gates || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function scorecardLaneGrid(items, idKey = "lane_id") {
  return `
    <div class="scorecard-mini-grid">
      ${items.map((item) => `
        <article class="runtime-scorecard-card">
          <div class="metric-head">
            <strong>${escapeHtml(item[idKey] || item.control_id || item.label || "lane")}</strong>
            <span class="state-pill ${escapeHtml(item.state || "research-candidate")}">${escapeHtml(pretty(item.state || "research-candidate"))}</span>
          </div>
          <small>${escapeHtml(item.label || "")}</small>
        </article>
      `).join("")}
    </div>
  `;
}

function renderMemoryProvenanceScorecard() {
  const scorecard = state.memoryProvenance || {};
  fill(dom.memoryProvenanceScorecard, `
    ${scorecardLaneGrid(scorecard.memory_lanes || [])}
    <div class="completion-scope">${escapeHtml(scorecard.quality_model?.answerability_gate || "source-backed-or-explicitly-unknown")}</div>
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderMemoryQualityScorecard() {
  const scorecard = state.memoryQuality || {};
  const latest = scorecard.latest_claim || {};
  const claims = scorecard.claims || [];
  fill(dom.memoryQualityScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.authority || "NexusBrain")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.quality_boundary || "source-backed or explicitly unknown")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.claim_count || 0)}</strong><small>claims</small></span>
        <span><strong>${escapeHtml(scorecard.verified_count || 0)}</strong><small>verified</small></span>
        <span><strong>${escapeHtml(scorecard.blocked_count || 0)}</strong><small>blocked</small></span>
      </div>
    </article>
    <div class="completion-scope">${escapeHtml(latest.claim_id || scorecard.consolidation_boundary || "No source-to-claim records yet")}</div>
    ${scorecardLaneGrid(claims.slice(0, 6).map((claim) => ({
      lane_id: claim.claim_id,
      label: `${claim.answerability_gate || "claim"} | ${claim.quality_state || "quality"} | ${claim.confidence || 0}`,
      state: claim.status || "static-canon",
    })))}
    <div class="token-grid">${(scorecard.research_lanes || []).map((lane) => `<span class="token">${escapeHtml(lane.lane_id)}</span>`).join("")}</div>
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderArtifactTrustScorecard() {
  const scorecard = state.artifactTrust || {};
  fill(dom.artifactTrustScorecard, `
    ${scorecardLaneGrid(scorecard.supply_chain_controls || [], "control_id")}
    <div class="completion-scope">${escapeHtml(scorecard.trust_rule || "no unsafe artifact without proof")}</div>
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderHardwareMatrixScorecard() {
  const scorecard = state.hardwareMatrix || {};
  fill(dom.hardwareMatrixScorecard, `
    ${scorecardLaneGrid(scorecard.deployment_lanes || [])}
    <div class="completion-scope">${escapeHtml(scorecard.fallback_rule || "certified accelerator or safe fallback")}</div>
  `);
}

function renderVisualOpsScorecard() {
  const scorecard = state.visualOps || {};
  fill(dom.visualOpsScorecard, `
    ${scorecardLaneGrid(scorecard.computer_use_lanes || [])}
    <div class="completion-scope">${escapeHtml(scorecard.safety_rule || "observe first; act only with approval")}</div>
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderToolExecutionScorecard() {
  const scorecard = state.toolExecution || {};
  fill(dom.toolExecutionScorecard, `
    ${scorecardLaneGrid(scorecard.execution_lanes || [])}
    <div class="completion-scope">${escapeHtml(scorecard.safe_execution_rule || "tools execute through NexusBrain policy and replay")}</div>
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderAssimilationTargetScorecard() {
  const scorecard = state.assimilationTargets || {};
  const targets = scorecard.targets || [];
  const skillTarget = targets.find((target) => target.target_id === "skill-system-orchestrator") || {};
  fill(dom.assimilationTargetScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.surface_id || "claude-code-assimilation-targets")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "live-bound")}">${escapeHtml(pretty(scorecard.runtime_state || "live-bound"))}</span>
      </div>
      <small>${escapeHtml((scorecard.coverage_summary || {}).clean_room_boundary || "source-backed public assimilation only")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.target_count || targets.length || 0)}</strong><small>targets</small></span>
        <span><strong>${escapeHtml((scorecard.coverage_summary || {}).live_bound_count || 0)}</strong><small>live bound</small></span>
        <span><strong>${escapeHtml((scorecard.source_refs || []).length || 0)}</strong><small>sources</small></span>
      </div>
    </article>
    ${scorecardLaneGrid(targets.slice(0, 10), "target_id")}
    <div class="completion-scope">${escapeHtml(skillTarget.assimilation_goal || "Skill Systems Orchestrator wires focused skills into end-to-end workflows.")}</div>
    <div class="token-grid">${(skillTarget.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
    <div class="token-grid">
      <span class="token">${escapeHtml((scorecard.operator_actions || {}).compose_skill_system?.endpoint || "/ops/brain/skill-systems/compose")}</span>
    </div>
  `);
}

function renderVideoAssimilationScorecard() {
  const scorecard = state.videoAssimilation || {};
  const targets = scorecard.targets || [];
  const coverage = scorecard.coverage_summary || {};
  fill(dom.videoAssimilationScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.surface_id || "video-assimilation-targets")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <small>${escapeHtml(scorecard.promotion_boundary || "source references stay refs-only until promotion gates pass")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.target_count || targets.length || 0)}</strong><small>targets</small></span>
        <span><strong>${escapeHtml(coverage.primary_verified_count || 0)}</strong><small>primary verified</small></span>
        <span><strong>${escapeHtml(coverage.shadow_only_count || 0)}</strong><small>shadow</small></span>
        <span><strong>${escapeHtml(coverage.clean_room_required_count || 0)}</strong><small>clean room</small></span>
      </div>
    </article>
    ${scorecardLaneGrid(targets.slice(0, 6).map((target) => ({
      target_id: target.target_id,
      label: target.label,
      state: target.promotion_state || target.source_status || "research-candidate",
    })), "target_id")}
  `);
}

function renderRetrievalPlannerScorecard() {
  const scorecard = state.retrievalPlanner || {};
  fill(dom.retrievalPlannerScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.surface_id || "retrieval-planner")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.plan_count || 0)}</strong><small>plans</small></span>
        <span><strong>${escapeHtml(scorecard.blocked_count || 0)}</strong><small>blocked</small></span>
        <span><strong>${escapeHtml((scorecard.required_controls || []).length || 0)}</strong><small>controls</small></span>
      </div>
      <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
    </article>
  `);
}

function renderOperatorEventsScorecard() {
  const scorecard = state.operatorEvents || {};
  const latest = scorecard.latest_event || {};
  fill(dom.operatorEventsScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.surface_id || "operator-events")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.event_count || 0)}</strong><small>events</small></span>
        <span><strong>${escapeHtml(scorecard.blocked_count || 0)}</strong><small>blocked</small></span>
        <span><strong>${escapeHtml(latest.permission_scope || "pending")}</strong><small>scope</small></span>
      </div>
      <div class="completion-scope">${escapeHtml(latest.event_stream_contract || "observation-plan-action-result-correction")}</div>
    </article>
  `);
}

function renderConceptTelemetryScorecard() {
  const scorecard = state.conceptTelemetry || {};
  fill(dom.conceptTelemetryScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.surface_id || "concept-telemetry")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "static-canon")}">${escapeHtml(pretty(scorecard.runtime_state || "static-canon"))}</span>
      </div>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.concept_count || 0)}</strong><small>concepts</small></span>
        <span><strong>${escapeHtml(scorecard.sae_experiment_count || 0)}</strong><small>sae experiments</small></span>
        <span><strong>${escapeHtml((scorecard.concepts || []).filter((item) => item.status === "blocked").length)}</strong><small>blocked</small></span>
      </div>
      <div class="completion-scope">${escapeHtml((scorecard.latest_concept || {}).manifold_caution_label || "behavioral proxies are not closed-model internals")}</div>
    </article>
  `);
}

function renderHiveNeuralSubstrateScorecard() {
  const scorecard = state.hiveNeuralSubstrate || {};
  const planes = scorecard.planes || [];
  const latest = scorecard.latest_forward_pass || {};
  const latestCandidate = scorecard.latest_candidate || {};
  const releaseLedger = scorecard.release_ledger || {};
  const globalFederationReviewLedger = scorecard.global_federation_review_ledger || {};
  const runtimeGrowth = scorecard.runtime_growth || {};
  const latestRuntimeGrowthReceipt = scorecard.latest_runtime_growth_receipt || runtimeGrowth.latest_runtime_receipt || {};
  const latestRuntimeGrowthPacket = scorecard.latest_runtime_growth_packet || latestRuntimeGrowthReceipt.federated_packet || {};
  const actions = scorecard.operator_actions || {};
  fill(dom.hiveNeuralSubstrateScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.control_panel_label || "Hive Neural Substrate v0")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "live-bound")}">${escapeHtml(pretty(scorecard.runtime_state || "live-bound"))}</span>
      </div>
      <small>${escapeHtml(scorecard.substrate_boundary || "graph-recurrent-sparse-moe-memory-harness-not-weight-training-yet")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.plane_count || planes.length || 16)}</strong><small>planes</small></span>
        <span><strong>${escapeHtml(scorecard.node_count || 0)}</strong><small>nodes</small></span>
        <span><strong>${escapeHtml((scorecard.required_controls || []).length || 0)}</strong><small>controls</small></span>
        <span><strong>${escapeHtml(releaseLedger.blocked_active_release_count || 0)}</strong><small>blocked active releases</small></span>
        <span><strong>${escapeHtml(releaseLedger.rolled_back_count || 0)}</strong><small>rolled back releases</small></span>
        <span><strong>${escapeHtml(globalFederationReviewLedger.blocked_count || 0)}</strong><small>blocked federation reviews</small></span>
        <span><strong>${escapeHtml(runtimeGrowth.runtime_interaction_count || 0)}</strong><small>native runtime growth bridge</small></span>
        <span><strong>${escapeHtml(latestRuntimeGrowthReceipt.surface_id || "no-native-growth-receipt")}</strong><small>native growth receipt</small></span>
        <span><strong>${escapeHtml(latestRuntimeGrowthPacket.surface_id || "no-native-growth-packet")}</strong><small>native shared growth packet</small></span>
      </div>
    </article>
    ${scorecardLaneGrid(planes.slice(0, 8).map((plane) => ({
      lane_id: plane.plane_id,
      title: plane.label,
      summary: plane.purpose,
    })))}
    <div class="completion-scope">${escapeHtml(latest.run_id || latestCandidate.candidate_id || "No hive forward pass or candidate yet")}</div>
    ${renderHiveNeuralSubstrateReplayDrilldown()}
    <div class="token-grid">${(scorecard.required_controls || ["recurrent_deliberation_loop", "checkpoint_before_write", "sandbox_eval_before_assimilation"]).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
    <div class="token-grid">${Object.entries(actions).map(([action, contract]) => `<span class="token">${escapeHtml(pretty(action))}: ${escapeHtml(contract.endpoint || "")}</span>`).join("")}</div>
  `);
}

function renderHiveNeuralSubstrateReplayDrilldown() {
  const replay = state.hiveNeuralSubstrateReplay || {};
  const control = replay.control_panel_replay || {};
  const chains = control.available_chains || [];
  const sensoryInputChain = replay.sensory_input_chain || [];
  const embeddingTensorChain = replay.embedding_tensor_chain || [];
  const temporalPositionalChain = replay.temporal_positional_chain || [];
  const memoryEngramChain = replay.memory_engram_chain || [];
  const attentionRoutingChain = replay.attention_routing_chain || [];
  const residualNormalizationChain = replay.residual_normalization_chain || [];
  const sparseExpertGateChain = replay.sparse_expert_gate_chain || [];
  const feedforwardExpertChain = replay.feedforward_expert_chain || [];
  const laminarMicrocircuitChain = replay.laminar_microcircuit_chain || [];
  const neuralPathwayChain = replay.neural_pathway_chain || [];
  const synapticTransmissionChain = replay.synaptic_transmission_chain || [];
  const neuroplasticWeightChain = replay.neuroplastic_weight_chain || [];
  const neuromodulatoryStateChain = replay.neuromodulatory_state_chain || [];
  const latentLoopExitChain = replay.latent_loop_exit_chain || [];
  const kvCacheCompressionChain = replay.kv_cache_compression_chain || [];
  const lossBackpropagationChain = replay.loss_backpropagation_chain || [];
  const optimizerSchoolChain = replay.optimizer_school_chain || [];
  const runtimeChain = replay.downstream_runtime_chain || [];
  const actionOutputDecoderChain = replay.action_output_decoder_chain || [];
  const forwardPropagationChain = replay.forward_propagation_chain || [];
  const backwardPropagationChain = replay.backward_propagation_chain || [];
  const parameterTensorChain = replay.parameter_tensor_chain || [];
  const activationFunctionChain = replay.activation_function_chain || [];
  const computationalGraphChain = replay.computational_graph_chain || [];
  const optimizerStateVectorChain = replay.optimizer_state_vector_chain || [];
  const modelGenomeChain = replay.model_genome_chain || [];
  const tensorRuntimeKernelChain = replay.tensor_runtime_kernel_chain || [];
  const layerBlockStackChain = replay.layer_block_stack_chain || [];
  const distillationLoopChain = replay.distillation_loop_chain || [];
  const federatedInfluenceChain = replay.federated_influence_chain || [];
  const executableDreamCycleChain = replay.executable_dream_cycle_chain || [];
  const deepReplayDrilldownChain = replay.deep_replay_drilldown_chain || [];
  const durableStorageChain = replay.durable_storage_chain || [];
  const checkpointCoverageChain = replay.checkpoint_coverage_chain || [];
  const runtimeDecisionChain = replay.runtime_decision_chain || [];
  const backendQuantizationExecutionChain = replay.backend_quantization_execution_chain || [];
  const nodeOutputs = replay.node_output_chain || [];
  const toolRegistryChain = replay.tool_execution_registry_chain || [];
  const taskGraphChain = replay.task_dependency_graph_chain || [];
  const providerCircuitChain = replay.provider_circuit_breaker_chain || [];
  const promptOverlayChain = replay.prompt_overlay_registry_chain || [];
  const skillSystemChain = replay.skill_system_loader_chain || [];
  const bridgeManagerChain = replay.bridge_manager_chain || [];
  const researchMonitorChain = replay.research_monitor_pipeline_chain || [];
  const activeReleaseChain = replay.active_release_chain || [];
  const projectHeartbeatChain = replay.project_heartbeat_chain || replay.project_heartbeat_replay_chain || [];
  const latestProjectHeartbeat = projectHeartbeatChain[0]
    || state.releaseWrapperRuntime?.project_heartbeat
    || state.controlPanel?.project_heartbeat
    || {};
  const failureRecoveryGovernance = latestProjectHeartbeat.failure_recovery_governance || {};
  return `
    <div class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>Replay Drilldown</strong>
        <span class="state-pill ${escapeHtml(control.available ? "live-bound" : "static-canon")}">${escapeHtml(control.available ? "Read only" : "No replay")}</span>
      </div>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(replay.run_count || 0)}</strong><small>runs</small></span>
        <span><strong>${escapeHtml(sensoryInputChain.length)}</strong><small>sense</small></span>
        <span><strong>${escapeHtml(embeddingTensorChain.length)}</strong><small>embeds</small></span>
        <span><strong>${escapeHtml(temporalPositionalChain.length)}</strong><small>pos</small></span>
        <span><strong>${escapeHtml(memoryEngramChain.length)}</strong><small>memory</small></span>
        <span><strong>${escapeHtml(attentionRoutingChain.length)}</strong><small>heads</small></span>
        <span><strong>${escapeHtml(residualNormalizationChain.length)}</strong><small>norms</small></span>
        <span><strong>${escapeHtml(sparseExpertGateChain.length)}</strong><small>gates</small></span>
        <span><strong>${escapeHtml(feedforwardExpertChain.length)}</strong><small>ffn</small></span>
        <span><strong>${escapeHtml(laminarMicrocircuitChain.length)}</strong><small>circuits</small></span>
        <span><strong>${escapeHtml(neuralPathwayChain.length)}</strong><small>paths</small></span>
        <span><strong>${escapeHtml(synapticTransmissionChain.length)}</strong><small>signals</small></span>
        <span><strong>${escapeHtml(neuroplasticWeightChain.length)}</strong><small>weights</small></span>
        <span><strong>${escapeHtml(neuromodulatoryStateChain.length)}</strong><small>gates</small></span>
        <span><strong>${escapeHtml(latentLoopExitChain.length)}</strong><small>loops</small></span>
        <span><strong>${escapeHtml(kvCacheCompressionChain.length)}</strong><small>kv</small></span>
        <span><strong>${escapeHtml(lossBackpropagationChain.length)}</strong><small>backprop</small></span>
        <span><strong>${escapeHtml(optimizerSchoolChain.length)}</strong><small>school</small></span>
        <span><strong>${escapeHtml(runtimeChain.length)}</strong><small>runtimes</small></span>
        <span><strong>${escapeHtml(actionOutputDecoderChain.length)}</strong><small>decode</small></span>
        <span><strong>${escapeHtml(forwardPropagationChain.length)}</strong><small>prop</small></span>
        <span><strong>${escapeHtml(backwardPropagationChain.length)}</strong><small>revprop</small></span>
        <span><strong>${escapeHtml(parameterTensorChain.length)}</strong><small>params</small></span>
        <span><strong>${escapeHtml(activationFunctionChain.length)}</strong><small>acts</small></span>
        <span><strong>${escapeHtml(computationalGraphChain.length)}</strong><small>ops</small></span>
        <span><strong>${escapeHtml(optimizerStateVectorChain.length)}</strong><small>opt</small></span>
        <span><strong>${escapeHtml(modelGenomeChain.length)}</strong><small>genes</small></span>
        <span><strong>${escapeHtml(tensorRuntimeKernelChain.length)}</strong><small>kernels</small></span>
        <span><strong>${escapeHtml(layerBlockStackChain.length)}</strong><small>blocks</small></span>
        <span><strong>${escapeHtml(distillationLoopChain.length)}</strong><small>teach</small></span>
        <span><strong>${escapeHtml(federatedInfluenceChain.length)}</strong><small>fed</small></span>
        <span><strong>${escapeHtml(executableDreamCycleChain.length)}</strong><small>dream</small></span>
        <span><strong>${escapeHtml(deepReplayDrilldownChain.length)}</strong><small>replay</small></span>
        <span><strong>${escapeHtml(durableStorageChain.length)}</strong><small>store</small></span>
        <span><strong>${escapeHtml(checkpointCoverageChain.length)}</strong><small>rewind</small></span>
        <span><strong>${escapeHtml(runtimeDecisionChain.length)}</strong><small>decide</small></span>
        <span><strong>${escapeHtml(backendQuantizationExecutionChain.length)}</strong><small>bench</small></span>
        <span><strong>${escapeHtml(nodeOutputs.length)}</strong><small>outputs</small></span>
        <span><strong>${escapeHtml(toolRegistryChain.length)}</strong><small>tools</small></span>
        <span><strong>${escapeHtml(taskGraphChain.length)}</strong><small>graphs</small></span>
        <span><strong>${escapeHtml(providerCircuitChain.length)}</strong><small>providers</small></span>
        <span><strong>${escapeHtml(promptOverlayChain.length)}</strong><small>prompts</small></span>
        <span><strong>${escapeHtml(skillSystemChain.length)}</strong><small>skills</small></span>
        <span><strong>${escapeHtml(bridgeManagerChain.length)}</strong><small>bridges</small></span>
        <span><strong>${escapeHtml(researchMonitorChain.length)}</strong><small>research</small></span>
        <span><strong>${escapeHtml(activeReleaseChain.length)}</strong><small>active</small></span>
        <span class="native-heartbeat-recovery-governance"><strong>${escapeHtml(failureRecoveryGovernance.status || "not-emitted")}</strong><small>native heartbeat recovery governance</small></span>
      </div>
      <div class="token-grid">${chains.map((chain) => `<span class="token">${escapeHtml(pretty(chain))}</span>`).join("")}</div>
    </div>
  `;
}

function renderSandboxAgentFactoryScorecard() {
  const scorecard = state.sandboxAgentFactory || {};
  const latest = scorecard.latest_run || {};
  const actions = scorecard.operator_actions || {};
  fill(dom.sandboxAgentFactoryScorecard, `
    <article class="runtime-scorecard-card">
      <div class="metric-head">
        <strong>${escapeHtml(scorecard.control_panel_label || "Sandbox Agent Factory")}</strong>
        <span class="state-pill ${escapeHtml(scorecard.runtime_state || "live-bound")}">${escapeHtml(pretty(scorecard.runtime_state || "live-bound"))}</span>
      </div>
      <small>${escapeHtml(scorecard.factory_boundary || "nexus-native-sandbox-agent-orchestration-not-direct-package-dependency")}</small>
      <div class="mini-metrics">
        <span><strong>${escapeHtml(scorecard.run_count || 0)}</strong><small>runs</small></span>
        <span><strong>${escapeHtml(scorecard.blocked_count || 0)}</strong><small>blocked</small></span>
        <span><strong>${escapeHtml((scorecard.required_controls || []).length || 0)}</strong><small>controls</small></span>
      </div>
    </article>
    ${scorecardLaneGrid((scorecard.architecture_contract || []).map((item) => ({
      lane_id: item,
      title: pretty(item),
      summary: "AFK sandbox factory control",
    })))}
    <div class="completion-scope">${escapeHtml(latest.run_id || "No sandbox factory run yet")}</div>
    <div class="token-grid">${(scorecard.required_controls || ["worktree_per_agent", "sandbox_provider_abstraction", "merge_back_policy_gate"]).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
    <div class="token-grid">${Object.entries(actions).map(([action, contract]) => `<span class="token">${escapeHtml(pretty(action))}: ${escapeHtml(contract.endpoint || "")}</span>`).join("")}</div>
  `);
}

function renderOutputDeliveryScorecard() {
  const scorecard = state.outputDelivery || {};
  fill(dom.outputDeliveryScorecard, `
    ${scorecardLaneGrid(scorecard.delivery_lanes || [])}
    <div class="completion-scope">${escapeHtml(scorecard.delivery_rule || "outputs require source evidence, artifact trust, memory feedback, and replay proof")}</div>
    <div class="token-grid">${(scorecard.required_controls || []).map((item) => `<span class="token">${escapeHtml(pretty(item))}</span>`).join("")}</div>
  `);
}

function renderSourceDocs() {
  const docs = state.controlPanel?.source_documents || [];
  dom.sourceDocs.innerHTML = docs
    .map((doc) => `<div class="ref-row">${escapeHtml(doc)}</div>`)
    .join("");
}

function renderCockpit() {
  const controlPanel = state.controlPanel || {};
  const cockpit = controlPanel.cockpit || {};
  const commandBar = cockpit.command_bar || {};
  const alertRail = cockpit.alert_rail || {};
  const timeline = cockpit.timeline || {};
  const operationsBoard = cockpit.operations_board || {};
  const liveColumns = operationsBoard.live_columns || [];
  const liveEvents = timeline.events || [];
  const pages = controlPanel.pages || [];
  const hiveMind = controlPanel.hive_mind || {};
  const commandChain = cockpit.command_chain || ["NexusBrain", "AO Hive", "Experts", "Tools/Outputs", "Memory Feedback", "NexusBrain"];
  const commandChainText = commandChain.join(" -> ");

  fill(dom.cockpitModeTabs, (cockpit.modes || [])
    .map((mode) => {
      const active = mode === (cockpit.primary_mode || "Command") ? " active" : "";
      return `<button class="mode-tab${active}" type="button">${escapeHtml(mode)}</button>`;
    })
    .join(""));

  fill(dom.cockpitCommandActions, listItems((cockpit.command_rail || {}).actions || [
    "Refresh live state",
    "Open wrapper",
    "Open visualizer",
  ]));

  fill(dom.cockpitCommandChain, escapeHtml(commandChainText));

  fill(dom.cockpitStats, [
    ["authority", commandBar.authority || "NexusBrain"],
    ["mode", cockpit.primary_mode || "Command"],
    ["active surface", activePage()?.label || "Overview"],
    ["pages", controlPanel.page_count || pages.length],
    ["mini brains", (hiveMind.mini_brain_nodes || []).length],
    ["command", commandBar.active_command_id || "standby"],
    ["trace", commandBar.session_trace || "standby"],
  ].map(([key, value]) => `
    <div class="metric">
      <small>${escapeHtml(key)}</small>
      <strong>${escapeHtml(valueText(value))}</strong>
    </div>
  `).join(""));

  const columnSignals = [
    ["NexusBrain orders", commandBar.primary_order || "orchestrate NexusNet"],
    ["AO local reasoning", "department-level planning and routing"],
    ["Expert evidence", "domain proof, tool fit, eval support"],
    ["Veto / escalation", "security, policy, uncertainty, conflict"],
    ["Execution status", "tool runs, artifacts, outputs, memory feedback"],
  ];
  const columns = liveColumns.length
    ? liveColumns
    : (operationsBoard.columns || columnSignals.map(([label]) => label)).map((column, index) => ({
        label: column,
        detail: columnSignals[index]?.[1] || "live cockpit lane",
        state: index === 0 ? "live-bound" : "static-canon",
        signal_type: index === 0 ? "command_issued" : "standby",
      }));
  fill(dom.cockpitOperationsBoard, columns
    .map((column, index) => `
      <article class="ops-column">
        <strong>${escapeHtml(column.label || columnSignals[index]?.[0] || "Operation")}</strong>
        <small>${escapeHtml(column.detail || column.actor || "live cockpit lane")}</small>
        <span class="state-pill ${escapeHtml(column.state || "static-canon")}">${escapeHtml(pretty(column.signal_type || column.state || "ready"))}</span>
      </article>
    `)
    .join(""));

  fill(dom.cockpitAlertRail, (alertRail.channels || [])
    .map((channel) => {
      const linkedPage = pages.find((page) => page.label.toLowerCase().includes(channel.split(" ")[0]));
      const stateValue = linkedPage?.state || (channel.includes("security") ? "live-bound" : "static-canon");
      return `
        <div class="alert-row ${escapeHtml(stateValue)}">
          <strong>${escapeHtml(channel)}</strong>
          <span class="state-pill ${escapeHtml(stateValue)}">${escapeHtml(pretty(stateValue))}</span>
        </div>
      `;
    })
    .join(""));

  fill(dom.cockpitGateMini, (controlPanel.build_gates || [])
    .map((gate) => `
      <div class="lane-row">
        <div class="metric-head">
          <strong>${escapeHtml(gate.gate_id || gate.label)}</strong>
          <span class="state-pill ${escapeHtml(gate.state || "static-canon")}">${escapeHtml(pretty(gate.state || "static-canon"))}</span>
        </div>
      </div>
    `)
    .join(""));

  const timelineItems = liveEvents.length
    ? liveEvents.map((event) => ({
        label: event.label || pretty(event.event_type),
        detail: event.actor || event.detail || event.event_type,
        event_type: event.event_type,
      }))
    : (timeline.lanes || []).map((lane) => ({ label: lane, detail: "standby", event_type: "lane" }));
  fill(dom.cockpitTimeline, timelineItems
    .map((item, index) => `
      <div class="timeline-node">
        <small>${escapeHtml(String(index + 1).padStart(2, "0"))}</small>
        <strong>${escapeHtml(item.label)}</strong>
        <span>${escapeHtml(item.detail)}</span>
      </div>
    `)
    .join(""));
}

function renderCanonRealization() {
  const realization = state.controlPanel?.canon_realization || {};
  const coverage = realization.coverage || {};
  const liveBindings = realization.live_bindings || {};
  const blockingItems = realization.blocking_items || [];
  const operatorQuestions = Object.entries(realization.operator_questions || {});
  const cards = [
    {
      label: "Required Surfaces",
      value: coverage.required_surface_count ?? 0,
      detail: `${coverage.missing_required_surface_count ?? 0} missing`,
      state: (coverage.missing_required_surface_count || 0) === 0 ? "live-bound" : "degraded",
    },
    {
      label: "Live Bound",
      value: coverage.live_bound_surface_count ?? 0,
      detail: "runtime-backed surfaces",
      state: "live-bound",
    },
    {
      label: "Research Candidates",
      value: coverage.research_candidate_surface_count ?? 0,
      detail: "gated before promotion",
      state: "research-candidate",
    },
    {
      label: "Active Command",
      value: liveBindings.active_command_id || "standby",
      detail: liveBindings.operation_state || "standby",
      state: liveBindings.active_command_id ? "live-bound" : "static-canon",
    },
  ];
  const questionRows = operatorQuestions.map(([questionId, item]) => `
    <div class="ledger-row">
      <strong>${escapeHtml(pretty(questionId))}</strong>
      <small>${escapeHtml(item.prompt || "Operator question")}</small>
      <span class="state-pill ${escapeHtml(item.answer_state || "static-canon")}">${escapeHtml(pretty(item.answer_state || "static-canon"))}</span>
    </div>
  `).join("");
  const blockers = blockingItems.slice(0, 5).map((item) => `
    <div class="ledger-row">
      <strong>${escapeHtml(item.surface_id)}</strong>
      <span class="state-pill ${escapeHtml(item.state)}">${escapeHtml(pretty(item.state))}</span>
      <small>${escapeHtml(item.next_action)}</small>
    </div>
  `).join("");
  fill(dom.canonRealizationLedger, `
    ${cards.map((card) => `
      <article class="ledger-card">
        <small>${escapeHtml(card.label)}</small>
        <strong>${escapeHtml(valueText(card.value))}</strong>
        <span class="state-pill ${escapeHtml(card.state)}">${escapeHtml(card.detail)}</span>
      </article>
    `).join("")}
    <article class="ledger-panel">
      <div class="metric-head">
        <strong>Operator Questions</strong>
        <span>${escapeHtml(String(operatorQuestions.length))}</span>
      </div>
      ${questionRows}
    </article>
    <article class="ledger-panel">
      <div class="metric-head">
        <strong>Open Realization Work</strong>
        <span>${escapeHtml(String(blockingItems.length))}</span>
      </div>
      ${blockers || '<div class="ledger-row"><strong>All required surfaces live-bound</strong></div>'}
    </article>
  `);
}

function renderCanonCompletion() {
  const completion = state.completion || state.controlPanel?.canon_realization?.completion_assessment || {};
  const gates = completion.gates || [];
  const percent = Number.isFinite(completion.completion_percent) ? completion.completion_percent : 0;
  const completionState = completion.ready_for_operator_use ? "live-bound" : "degraded";
  fill(dom.completionPercent, `${percent}%`);
  if (dom.completionState) {
    dom.completionState.className = `state-pill ${completionState}`;
    dom.completionState.textContent = completion.ready_for_operator_use ? "operator ready" : "blocked";
  }
  fill(
    dom.completionScope,
    `${pretty(completion.claim_scope || "canon-control-plane")} | full product finished: ${valueText(Boolean(completion.full_product_finished))}`,
  );
  fill(dom.canonCompletionMatrix, gates
    .map((gate) => {
      const blockers = gate.blockers || [];
      return `
        <article class="completion-card ${escapeHtml(gate.state || "static-canon")}">
          <div class="metric-head">
            <strong>${escapeHtml(gate.label || pretty(gate.gate_id))}</strong>
            <span class="state-pill ${escapeHtml(gate.state || "static-canon")}">${escapeHtml(pretty(gate.state || "static-canon"))}</span>
          </div>
          <small>${escapeHtml(gate.metric || "unmeasured")}</small>
          <div class="ref-row">${escapeHtml((gate.evidence_refs || []).slice(0, 4).join(" | ") || "no evidence")}</div>
          ${blockers.length ? `<div class="blocker-row">${escapeHtml(blockers.join(" | "))}</div>` : ""}
        </article>
      `;
    })
    .join(""));
}

function renderArchitectureMap() {
  const controlPanel = state.controlPanel || {};
  const pages = controlPanel.pages || [];
  const liveRefs = controlPanel.live_refs || {};
  const quantCatalog = controlPanel.quantization_catalog || {};
  const researchLanes = controlPanel.research_lanes || [];
  const hiveMind = controlPanel.hive_mind || {};
  const centralOrchestrator = hiveMind.central_orchestrator || {};
  const commandChain = centralOrchestrator.command_chain || [
    "NexusBrain",
    "AO Hive",
    "Experts",
    "Tools/Outputs",
    "Memory Feedback",
    "NexusBrain",
  ];
  const commandChainText = commandChain
    .map((item) => item === "Experts Hive" ? "Experts" : item)
    .map((item) => item === "Tools / Outputs" ? "Tools/Outputs" : item)
    .join(" -> ");

  fill(dom.inputGrid, [
    nodeHtml("User Commands", statusFor("input-ingestion"), "command"),
    nodeHtml("Uploaded Files", statusFor("input-ingestion"), "source"),
    nodeHtml("Project Notes", statusFor("input-ingestion"), "notes"),
    nodeHtml("Code Snippets", statusFor("input-ingestion"), "risk"),
    nodeHtml("Meeting Transcripts", statusFor("input-ingestion"), "redact"),
    nodeHtml("External APIs", statusFor("input-ingestion"), "trust"),
    nodeHtml("Webhooks / Events", statusFor("input-ingestion"), "event"),
    nodeHtml("Real-time Streams", statusFor("input-ingestion"), "freshness"),
  ].join(""));

  fill(dom.memoryGrid, listItems([
    labelFor("context-memory", "Context & Memory"),
    "Project State",
    "Continuity Packets",
    "Knowledge Graph",
    "Vector / Embedding Store",
    "Source-to-Claim Maps",
    "Memory Consolidation",
  ]));

  fill(dom.evolutionGrid, [
    nodeHtml("Dream / Simulate", statusFor("dreaming-evolution"), "background process"),
    nodeHtml("Reflect & Analyze", statusFor("governance-observability"), "self review"),
    nodeHtml("Forward Radar", statusFor("forward-radar"), "research watchlist"),
    nodeHtml("Eval & Score", statusFor("eval-center"), "promotion gate"),
    nodeHtml("Autonomous Updates", "shadow-only", "guarded loop"),
  ].join(""));

  fill(dom.orchestratorStrip, [
    nodeHtml(labelFor("live-flow-trace", "Intent Router"), statusFor("live-flow-trace"), "routes"),
    nodeHtml(labelFor("context-memory", "Context Retriever"), statusFor("context-memory"), "retrieves"),
    nodeHtml(labelFor("neural-core", "Planning Engine"), statusFor("neural-core"), "plans"),
    nodeHtml("Reasoning Engine", statusFor("neural-core"), "reasons"),
    nodeHtml("Task Decomposer", statusFor("tools-execution"), "decomposes"),
    nodeHtml("Decision Manager", statusFor("governance-observability"), "decides"),
    nodeHtml("Goal Manager", statusFor("dreaming-evolution"), "evolves"),
    nodeHtml("Self-Check", statusFor("eval-center"), "reviews"),
  ].join(""));

  fill(dom.aoHiveStrip, [
    nodeHtml("Systems Architect AO", statusFor("ao-hive"), "proposal"),
    nodeHtml("Senior Engineer AO", statusFor("ao-hive"), "evidence"),
    nodeHtml("Product Strategy AO", statusFor("ao-hive"), "priority"),
    nodeHtml("Security AO", statusFor("governance-observability"), "veto"),
    nodeHtml("Integration AO", statusFor("connections-protocols"), "route"),
    nodeHtml("Recursive Learning AO", statusFor("dreaming-evolution"), "collective action"),
  ].join(""));

  fill(dom.coreMetrics, [
    ["pages", controlPanel.page_count || pages.length || 0],
    ["live refs", Object.keys(liveRefs).length],
    ["research lanes", researchLanes.length],
    ["quant methods", (quantCatalog.method_families || []).length],
    ["hive model", hiveMind.label || "Commanded Collective Hive"],
    ["active surface", activePage()?.label || "none"],
    ["brain state", activePage()?.state || "unknown"],
  ].map(([key, value]) => `
    <div class="metric">
      <small>${escapeHtml(key)}</small>
      <strong>${escapeHtml(valueText(value))}</strong>
    </div>
  `).join(""));

  fill(dom.hiveCommandChain, escapeHtml(commandChainText));
  fill(dom.hiveCommandChainDetail, escapeHtml(commandChainText));
  const hybridTraits = hiveMind.hybrid_traits || {};
  fill(dom.hiveTraitGrid, Object.entries(hybridTraits)
    .flatMap(([trait, values]) => [
      `<span class="token trait-head">${escapeHtml(pretty(trait))}</span>`,
      ...(Array.isArray(values) ? values : []).map((value) => `<span class="token">${escapeHtml(value)}</span>`),
    ])
    .join(""));
  fill(dom.hiveSignalGrid, (hiveMind.mini_brain_signal_contract || [])
    .map((signal) => `<span class="token">${escapeHtml(signalLabel(signal))}</span>`)
    .join(""));
  fill(dom.miniBrainGrid, (hiveMind.mini_brain_nodes || [])
    .map((node) => `
      <article class="mini-brain-card ${escapeHtml(node.state || "static-canon")}">
        <div class="metric-head">
          <strong>${escapeHtml(node.role)}</strong>
          <span class="state-pill ${escapeHtml(node.state || "static-canon")}">${escapeHtml(pretty(node.state || "static-canon"))}</span>
        </div>
        <p>${escapeHtml(node.scope || "")}</p>
        <small>Reports to ${escapeHtml(node.reports_to || "NexusBrain")}</small>
        <div class="token-grid">
          ${(node.signals || []).map((signal) => `<span class="token">${escapeHtml(signalLabel(signal))}</span>`).join("")}
        </div>
      </article>
    `)
    .join(""));

  fill(dom.executionStrip, [
    nodeHtml(labelFor("tools-execution", "Documentation Agent"), statusFor("tools-execution"), "tool interface"),
    nodeHtml("Code Agent", statusFor("tools-execution"), "execution"),
    nodeHtml("Planning Agent", statusFor("neural-core"), "planning"),
    nodeHtml("Research Agent", statusFor("forward-radar"), "radar"),
    nodeHtml("Data Agent", statusFor("context-memory"), "memory"),
    nodeHtml("Integration Agent", statusFor("communication-integration"), "channels"),
  ].join(""));

  fill(dom.buildStrip, [
    nodeHtml("Code Generation", statusFor("tools-execution"), "build"),
    nodeHtml("API Design", statusFor("communication-integration"), "contract"),
    nodeHtml("Workflow Automation", statusFor("ao-hive"), "AO route"),
    nodeHtml("Test Plans", statusFor("eval-center"), "eval"),
    nodeHtml("CI / CD Pipeline", statusFor("governance-observability"), "guarded"),
    nodeHtml("Artifact Trust", statusFor("artifact-trust"), "provenance"),
    nodeHtml("Runtime Lab", statusFor("runtime-lab"), "hardware"),
  ].join(""));

  fill(dom.outputStrip, [
    nodeHtml("Architecture Diagrams", statusFor("outputs-deliverables"), "map"),
    nodeHtml("Implementation Plans", statusFor("outputs-deliverables"), "plan"),
    nodeHtml("Source Code", statusFor("outputs-deliverables"), "code"),
    nodeHtml("Documentation", statusFor("outputs-deliverables"), "canon"),
    nodeHtml("Roadmaps", statusFor("outputs-deliverables"), "future"),
    nodeHtml("Reports & Analytics", statusFor("outputs-deliverables"), "observe"),
    nodeHtml("Exports & Packages", statusFor("outputs-deliverables"), "ship"),
  ].join(""));

  const experts = [
    ["Code", "coder"],
    ["API Design", "protocols"],
    ["DevOps", "runtime"],
    ["Database", "memory"],
    ["AI / ML", "models"],
    ["Data Analysis", "evals"],
    ["Testing", "quality"],
    ["Security", "policy"],
    ["UI / UX", "visualops"],
    ["Product", "strategy"],
    ["Legal", "compliance"],
    ["Custom", "extension"],
  ];
  fill(dom.expertGrid, experts.map(([label, detail]) => `
    <div class="expert-node ${escapeHtml(statusFor("experts-hive"))}">
      <strong>${escapeHtml(label)}</strong>
      <small>${escapeHtml(detail)}</small>
    </div>
  `).join(""));

  fill(dom.securityGrid, [
    "Security Rules",
    "Error Handling",
    "Logs",
    "Metrics",
    "Alerts",
    "Audit Trail",
    "Version Control",
    "Decision Records",
    "Compliance",
    "Privacy Controls",
  ].map((item) => `<div class="security-node">${escapeHtml(item)}</div>`).join(""));

  fill(dom.commsGrid, [
    nodeHtml("Webhooks", statusFor("communication-integration"), "trigger"),
    nodeHtml("Message Bus", statusFor("communication-integration"), "queue"),
    nodeHtml("Event Streams", statusFor("communication-integration"), "events"),
    nodeHtml("Real-time Sync", statusFor("communication-integration"), "state"),
    nodeHtml("MCP / A2A / ACP", statusFor("connections-protocols"), "protocol"),
    nodeHtml("AG-UI", statusFor("connections-protocols"), "ui events"),
    nodeHtml("Third-party Services", statusFor("communication-integration"), "adapter"),
    nodeHtml("Chat / Collaboration", statusFor("communication-integration"), "human loop"),
  ].join(""));

  fill(dom.systemPrinciples, listItems([
    "Modular & Extensible",
    "Context-Aware",
    "Secure by Design",
    "Observable & Transparent",
    "Reliable & Resilient",
    "Human-AI Collaboration",
    "Trust & Accountability",
    "Evolution is Continuous",
  ]));
}

function renderAll() {
  renderCockpit();
  renderCanonRealization();
  renderCanonCompletion();
  renderArchitectureMap();
  renderLegend();
  renderNav();
  renderGates();
  renderPage();
  renderRadar();
  renderRuntimeScorecard();
  renderEvolutionDossier();
  renderSelfImprovementScorecard();
  renderDevelopmentalCortexScorecard();
  renderSelfReviewScorecard();
  renderProtocolTrustScorecard();
  renderProtocolTrustRegistryScorecard();
  renderCommunicationIntegrationScorecard();
  renderInputIngestionScorecard();
  renderLiveFlowScorecard();
  renderNeuralCoreScorecard();
  renderObservabilityScorecard();
  renderGenAIObservabilityScorecard();
  renderSecurityGovernanceScorecard();
  renderPolicyKernelScorecard();
  renderAgenticPipelineScorecard();
  renderAgentOpportunityScorecard();
  renderHarnessProviderScorecard();
  renderHarnessRoutingScorecard();
  renderHarnessImprovementLedger();
  renderEdgeWorkloadRouterScorecard();
  renderMultimodalComputerUseScorecard();
  renderInferenceEconomyRouterScorecard();
  renderInferenceArchitectureScorecard();
  renderCacheLedgerScorecard();
  renderRuntimeWorkloadScorecards();
  renderQuantizationCatalogScorecard();
  renderBrowserContextScorecard();
  renderEngramMemoryScorecard();
  renderDatasetRadarScorecard();
  renderDatasetForgeScorecard();
  renderKnowledgeArtifactsScorecard();
  renderAdapterRegistryScorecard();
  renderFineTuneDecisionGateScorecard();
  renderAdapterTrainingScorecard();
  renderGrowthEngineScorecard();
  renderProductionSpineScorecard();
  renderEvalRegistryScorecard();
  renderArtifactTrustRegistryScorecard();
  renderAutonomousUpdatesScorecard();
  renderBlackBoxRecorder();
  renderHiveConsensusScorecard();
  renderAoHiveScorecard();
  renderExpertsHiveScorecard();
  renderResearcherSwarmScorecard();
  renderForwardRadarScorecard();
  renderEvalSuiteScorecard();
  renderMemoryProvenanceScorecard();
  renderMemoryQualityScorecard();
  renderArtifactTrustScorecard();
  renderHardwareMatrixScorecard();
  renderVisualOpsScorecard();
  renderToolExecutionScorecard();
  renderAssimilationTargetScorecard();
  renderVideoAssimilationScorecard();
  renderRetrievalPlannerScorecard();
  renderOperatorEventsScorecard();
  renderConceptTelemetryScorecard();
  renderHiveNeuralSubstrateScorecard();
  renderSandboxAgentFactoryScorecard();
  renderOutputDeliveryScorecard();
  renderQuantCatalog();
  renderSourceDocs();
}

async function issueCanonCommand(event) {
  event.preventDefault();
  const commandText = (dom.canonCommandInput.value || "").trim();
  if (!commandText) {
    dom.canonCommandStatus.textContent = "Enter a command for NexusBrain first.";
    return;
  }
  dom.canonCommandButton.disabled = true;
  dom.canonCommandStatus.textContent = "Issuing command through NexusBrain authority...";
  try {
    const session = dom.sessionInput.value || sessionId();
    localStorage.setItem("nn_session", session);
    const payload = await fetchJSON("/ops/brain/operations/commands", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: session,
        command_text: commandText,
        priority: dom.canonCommandPriority.value || "normal",
        target_surface: "mission-control-cockpit",
        context: { source: "control-panel" },
      }),
    });
    dom.canonCommandInput.value = "";
    dom.canonCommandStatus.textContent = `Issued ${payload.command?.command_id || "NexusBrain command"}.`;
    await loadControlPanel();
  } catch (error) {
    dom.canonCommandStatus.textContent = error.message;
    setConnection("error", error.message);
  } finally {
    dom.canonCommandButton.disabled = false;
  }
}

async function realizeSelectedSurface() {
  const page = activePage();
  if (!page) {
    dom.realizeSurfaceStatus.textContent = "No selected surface to queue.";
    return;
  }
  dom.realizeSurfaceButton.disabled = true;
  dom.realizeSurfaceStatus.textContent = `Queueing ${page.label} through NexusBrain...`;
  try {
    const session = dom.sessionInput.value || sessionId();
    localStorage.setItem("nn_session", session);
    const payload = await fetchJSON("/ops/brain/canon/realize-next", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: session,
        surface_id: page.page_id,
      }),
    });
    dom.realizeSurfaceStatus.textContent = `Queued ${payload.command?.command_id || page.label}.`;
    await loadControlPanel();
  } catch (error) {
    dom.realizeSurfaceStatus.textContent = error.message;
    setConnection("error", error.message);
  } finally {
    dom.realizeSurfaceButton.disabled = false;
  }
}

async function recordAnswerProof(event) {
  event.preventDefault();
  const questionId = dom.canonProofQuestion.value;
  const detail = (dom.canonProofDetail.value || "").trim();
  if (!questionId || !detail) {
    dom.canonProofStatus.textContent = "Choose a Canon answer and enter proof detail first.";
    return;
  }
  dom.canonProofButton.disabled = true;
  dom.canonProofStatus.textContent = "Recording proof through NexusBrain...";
  try {
    const session = dom.sessionInput.value || sessionId();
    localStorage.setItem("nn_session", session);
    const payload = await fetchJSON(`/ops/brain/canon/answers/${encodeURIComponent(questionId)}/events`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: session,
        actor: dom.canonProofActor.value || "Operator",
        detail,
        metadata: { source: "control-panel-proof-form" },
      }),
    });
    dom.canonProofDetail.value = "";
    dom.canonProofStatus.textContent = `Recorded ${payload.event?.event_id || pretty(questionId)}.`;
    await loadControlPanel();
  } catch (error) {
    dom.canonProofStatus.textContent = error.message;
    setConnection("error", error.message);
  } finally {
    dom.canonProofButton.disabled = false;
  }
}

async function submitDatasetRadarRefresh(event) {
  event.preventDefault();
  const query = (dom.datasetRadarQuery?.value || "").trim();
  const sort = dom.datasetRadarSort?.value || "lastModified";
  const limit = Number(dom.datasetRadarLimit?.value || 10);
  const presetId = dom.datasetRadarPreset?.value || "coder-expert";
  const session = dom.sessionInput.value || sessionId();
  try {
    dom.datasetRadarRefreshButton.disabled = true;
    dom.datasetRadarRefreshStatus.textContent = "Refreshing Dataset Radar through NexusBrain gate...";
    const requestBody = {
      session_id: session,
      operator_actor: "Control Panel",
      source: "control-panel-dataset-radar-card",
      preset_id: presetId,
      sort,
      limit,
      ...datasetRadarDiscoveryFilters(),
    };
    if (query) {
      requestBody.query = query;
    }
    const payload = await fetchJSON("/ops/brain/dataset-radar/refresh", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestBody),
    });
    state.datasetRadarRefresh = payload;
    state.datasetRadar = await fetchJSON(canonScorecardEndpoints.datasetRadar);
    renderDatasetRadarScorecard();
    dom.datasetRadarRefreshStatus.textContent = `Captured ${payload.candidate_count || 0} candidates; auto approval disabled.`;
    setConnection("connected", "Dataset Radar refreshed");
  } catch (error) {
    dom.datasetRadarRefreshStatus.textContent = error.message;
    setConnection("error", error.message);
  } finally {
    dom.datasetRadarRefreshButton.disabled = false;
  }
}

async function runDatasetRadarPresetBatch() {
  const session = dom.sessionInput.value || sessionId();
  const limit = Number(dom.datasetRadarLimit?.value || 10);
  const presetIds = Array.from(dom.datasetRadarPreset?.options || []).map((option) => option.value).filter(Boolean);
  try {
    dom.datasetRadarBatchButton.disabled = true;
    dom.datasetRadarRefreshStatus.textContent = "Running Dataset Radar target-node preset batch...";
    const payload = await fetchJSON(canonScorecardEndpoints.datasetRadarRefreshBatch, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: session,
        operator_actor: "Control Panel",
        source: "control-panel-dataset-radar-batch",
        preset_ids: presetIds,
        limit,
        ...datasetRadarDiscoveryFilters(),
      }),
    });
    state.datasetRadarBatch = payload;
    state.datasetRadar = await fetchJSON(canonScorecardEndpoints.datasetRadar);
    renderDatasetRadarScorecard();
    dom.datasetRadarRefreshStatus.textContent = `Batch ${payload.batch_id || "refresh"} captured ${payload.candidate_count || 0} candidates; auto approval disabled.`;
    setConnection("connected", "Dataset Radar batch refreshed");
  } catch (error) {
    dom.datasetRadarRefreshStatus.textContent = error.message;
    setConnection("error", error.message);
  } finally {
    dom.datasetRadarBatchButton.disabled = false;
  }
}

async function submitDatasetRadarCandidateReview(event) {
  event.preventDefault();
  const datasetId = (dom.datasetRadarReviewDatasetId?.value || "").trim();
  if (!datasetId) {
    dom.datasetRadarRefreshStatus.textContent = "Enter a candidate dataset id before recording review.";
    return;
  }
  const session = dom.sessionInput.value || sessionId();
  const reviewState = dom.datasetRadarReviewState?.value || "approved_teacher_context";
  const reason = (dom.datasetRadarReviewReason?.value || "").trim() || "Control Panel candidate review.";
  try {
    dom.datasetRadarCandidateReviewButton.disabled = true;
    dom.datasetRadarRefreshStatus.textContent = "Recording Dataset Radar candidate review...";
    const payload = await fetchJSON(canonScorecardEndpoints.datasetRadarCandidateReview, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: session,
        operator_actor: "Control Panel",
        source: "control-panel-dataset-radar-candidate-review",
        dataset_id: datasetId,
        review_state: reviewState,
        reviewer: "operator",
        reason,
      }),
    });
    state.datasetRadarCandidateReview = payload;
    state.datasetRadar = await fetchJSON(canonScorecardEndpoints.datasetRadar);
    renderDatasetRadarScorecard();
    dom.datasetRadarRefreshStatus.textContent = `Recorded ${payload.applied_state || reviewState} review for ${payload.dataset_id || datasetId}; training approval remains blocked.`;
    setConnection("connected", "Dataset Radar candidate review recorded");
  } catch (error) {
    dom.datasetRadarRefreshStatus.textContent = error.message;
    setConnection("error", error.message);
  } finally {
    dom.datasetRadarCandidateReviewButton.disabled = false;
  }
}

async function submitDatasetRadarMaterialRequest(event) {
  event.preventDefault();
  const session = dom.sessionInput.value || sessionId();
  const requestedSplit = dom.datasetRadarMaterialSplit?.value || "teacher_context";
  const targetNode = (dom.datasetRadarMaterialTarget?.value || "").trim() || "Coder Expert";
  const teacherRef = (dom.datasetRadarMaterialTeacher?.value || "").trim() || "teacher:qwen3-coder-next";
  const limit = Number(dom.datasetRadarMaterialLimit?.value || 24);
  try {
    dom.datasetRadarMaterialRequestButton.disabled = true;
    dom.datasetRadarRefreshStatus.textContent = "Requesting gated teacher material through Dataset Radar...";
    const payload = await fetchJSON(canonScorecardEndpoints.datasetRadarMaterialRequest, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: session,
        operator_actor: "Control Panel",
        source: "control-panel-dataset-radar-material-request",
        teacher_ref: teacherRef,
        target_node: targetNode,
        requested_split: requestedSplit,
        allowed_use: requestedSplit,
        limit,
      }),
    });
    state.datasetRadarMaterialRequest = payload;
    state.datasetRadar = await fetchJSON(canonScorecardEndpoints.datasetRadar);
    renderDatasetRadarScorecard();
    dom.datasetRadarRefreshStatus.textContent = `Material request ${payload.material_request_id || "recorded"} approved ${(payload.approved_source_ids || []).length} sources for ${payload.requested_split || requestedSplit}.`;
    setConnection("connected", "Dataset Radar material request recorded");
  } catch (error) {
    dom.datasetRadarRefreshStatus.textContent = error.message;
    setConnection("error", error.message);
  } finally {
    dom.datasetRadarMaterialRequestButton.disabled = false;
  }
}

async function inspectDatasetRadarSourceDetail(event) {
  event?.preventDefault?.();
  const datasetId = (dom.datasetRadarSourceDetailDatasetId?.value || "").trim();
  if (!datasetId) {
    dom.datasetRadarRefreshStatus.textContent = "Enter a Dataset Radar source id before inspecting detail.";
    return;
  }
  try {
    dom.datasetRadarSourceDetailButton.disabled = true;
    dom.datasetRadarRefreshStatus.textContent = "Inspecting Dataset Radar source detail replay...";
    const sourcePath = datasetId.split("/").map((part) => encodeURIComponent(part)).join("/");
    const payload = await fetchJSON(`${canonScorecardEndpoints.datasetRadarSourceDetail}/${sourcePath}`);
    state.datasetRadarSourceDetail = payload;
    renderDatasetRadarScorecard();
    dom.datasetRadarRefreshStatus.textContent = `Source detail loaded for ${payload.dataset_id || datasetId}: ${payload.source_kind || "source"}.`;
    setConnection("connected", "Dataset Radar source detail loaded");
  } catch (error) {
    dom.datasetRadarRefreshStatus.textContent = error.message;
    setConnection("error", error.message);
  } finally {
    dom.datasetRadarSourceDetailButton.disabled = false;
  }
}

function inspectDatasetRadarSourceFromButton(event) {
  const button = event.target.closest("[data-dataset-radar-detail]");
  if (!button) {
    return;
  }
  dom.datasetRadarSourceDetailDatasetId.value = button.dataset.datasetRadarDetail || "";
  inspectDatasetRadarSourceDetail();
}

async function scanLatestKnowledgeArtifactTrust(event) {
  const button = event.target.closest("[data-kac-artifact-trust-scan]");
  if (!button) {
    return;
  }
  const artifactId = button.dataset.kacArtifactTrustScan || state.knowledgeArtifacts?.latest_artifact?.artifact_id || "";
  if (!artifactId) {
    setConnection("error", "No KAC artifact is available to scan.");
    return;
  }
  try {
    button.disabled = true;
    setConnection("", "Scanning KAC artifact through Artifact Trust...");
    const payload = await fetchJSON("/ops/brain/artifact-trust/knowledge-artifacts/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ artifact_id: artifactId }),
    });
    state.knowledgeArtifactTrustScan = payload;
    state.artifactTrustRegistry = await fetchJSON(canonScorecardEndpoints.artifactTrustRegistry);
    renderKnowledgeArtifactsScorecard();
    renderArtifactTrustRegistryScorecard();
    setConnection(
      payload.status === "quarantined" ? "error" : "connected",
      `KAC artifact trust scan ${payload.status || "completed"}`
    );
  } catch (error) {
    setConnection("error", error.message);
  } finally {
    button.disabled = false;
  }
}

async function submitDatasetForgeManifest(event) {
  event.preventDefault();
  try {
    dom.datasetForgeManifestButton.disabled = true;
    dom.datasetForgeManifestStatus.textContent = "Building DatasetForge manifest through gated operator form...";
    const payload = await fetchJSON(canonScorecardEndpoints.datasetForgeManifestBuild, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datasetForgeManifestRequestBody()),
    });
    state.datasetForgeManifest = payload;
    state.datasetForge = await fetchJSON(canonScorecardEndpoints.datasetForge);
    renderDatasetForgeScorecard();
    dom.datasetForgeManifestStatus.textContent = `Built ${payload.dataset_manifest_id || "DatasetForge manifest"} with status ${payload.status || "unknown"}.`;
    setConnection("connected", "DatasetForge manifest built");
  } catch (error) {
    dom.datasetForgeManifestStatus.textContent = error.message;
    setConnection("error", error.message);
  } finally {
    dom.datasetForgeManifestButton.disabled = false;
  }
}

async function loadControlPanel() {
  setConnection("", "Connecting");
  const session = dom.sessionInput.value || sessionId();
  const releaseWrapperStatus = await loadReleaseWrapperStatusCard(session).catch(() => null);
  const releaseWrapperSessionLifecycle = await loadReleaseWrapperSessionLifecycle(session).catch(() => null);
  renderReleaseWrapperStatusFallback(releaseWrapperStatus, releaseWrapperSessionLifecycle);
  const url = `/ops/brain/visualizer/state?session_id=${encodeURIComponent(session)}`;
  const payload = await fetchJSON(url);
  state.payload = payload;
  state.controlPanel = payload.overlay_state?.control_panel || null;
  if (!state.controlPanel) {
    throw new Error("control_panel payload missing from visualizer overlay");
  }
  state.completion = state.controlPanel.completion_assessment || state.controlPanel.canon_realization?.completion_assessment || null;
  state.runtimeScorecard = state.controlPanel.runtime_scorecard || null;
  state.evolutionDossier = state.controlPanel.evolution_dossier || null;
  state.selfImprovement = state.controlPanel.self_improvement_scorecard || null;
  state.developmentalCortex = state.controlPanel.developmental_cortex_scorecard || null;
  state.authoritySpine = state.controlPanel.authority_spine_scorecard || null;
  state.evidenceStore = state.controlPanel.evidence_store_scorecard || null;
  state.evalFederation = state.controlPanel.eval_federation_scorecard || null;
  state.toolActionHarness = state.controlPanel.tool_action_harness_scorecard || null;
  state.runtimeDecisionLedger = state.controlPanel.runtime_decision_ledger_scorecard || null;
  state.selfReview = state.controlPanel.self_review_scorecard || null;
  state.protocolTrust = state.controlPanel.protocol_trust_scorecard || null;
  state.protocolTrustRegistry = state.controlPanel.protocol_trust_registry_scorecard || null;
  state.communicationIntegration = state.controlPanel.communication_integration_scorecard || null;
  state.inputIngestion = state.controlPanel.input_ingestion_scorecard || null;
  state.liveFlow = state.controlPanel.live_flow_scorecard || null;
  state.neuralCore = state.controlPanel.neural_core_scorecard || null;
  state.observability = state.controlPanel.observability_scorecard || null;
  state.genAIObservability = state.controlPanel.genai_observability_scorecard || null;
  state.securityGovernance = state.controlPanel.security_governance_scorecard || null;
  state.policyKernel = state.controlPanel.policy_kernel_scorecard || null;
  state.agenticPipeline = state.controlPanel.agentic_pipeline_scorecard || null;
  state.agentOpportunity = state.controlPanel.agent_opportunity_scorecard || null;
  state.harnessProvider = state.controlPanel.harness_provider_scorecard || null;
  state.harnessRouting = state.controlPanel.harness_routing_scorecard || null;
  state.harnessImprovementLedger = state.controlPanel.harness_improvement_ledger || null;
  state.edgeWorkloadRouter = state.controlPanel.edge_workload_router_scorecard || null;
  state.multimodalComputerUse = state.controlPanel.multimodal_computer_use_scorecard || null;
  state.inferenceEconomyRouter = state.controlPanel.inference_economy_router_scorecard || null;
  state.inferenceArchitecture = state.controlPanel.inference_architecture_scorecard || null;
  state.cacheLedger = state.controlPanel.cache_ledger_scorecard || null;
  state.runtimeWorkloadScorecards = state.controlPanel.runtime_workload_scorecards || null;
  state.quantizationCatalogScorecard = state.controlPanel.quantization_catalog_scorecard || null;
  state.browserContext = state.controlPanel.browser_context_scorecard || null;
  state.engramMemory = state.controlPanel.engram_memory_scorecard || null;
  state.datasetRadar = state.controlPanel.dataset_radar_scorecard || null;
  state.datasetForge = state.controlPanel.dataset_forge_scorecard || null;
  state.knowledgeArtifacts = state.controlPanel.knowledge_artifacts_scorecard || null;
  state.adapterRegistry = state.controlPanel.adapter_registry_scorecard || null;
  state.fineTuneDecisionGate = state.controlPanel.fine_tune_decision_gate_scorecard || null;
  state.adapterTraining = state.controlPanel.adapter_training_scorecard || null;
  state.growthEngine = state.controlPanel.growth_engine_scorecard || null;
  state.productionSpine = state.controlPanel.production_spine_scorecard || null;
  state.evalRegistry = state.controlPanel.eval_registry_scorecard || null;
  state.artifactTrustRegistry = state.controlPanel.artifact_trust_registry_scorecard || null;
  state.autonomousUpdates = state.controlPanel.autonomous_update_scorecard || null;
  state.releaseWrapperRuntime = state.controlPanel.release_wrapper_runtime || null;
  state.releaseHarnessRuntime = state.controlPanel.release_harness_runtime || state.releaseWrapperRuntime || null;
  state.cluster9TeacherReconciliation = state.controlPanel.cluster9_teacher_reconciliation
    || state.releaseHarnessRuntime?.cluster9_teacher_reconciliation
    || state.releaseWrapperRuntime?.cluster9_teacher_reconciliation
    || null;
  state.releaseWrapperTelemetry = state.controlPanel.release_wrapper_telemetry || state.releaseWrapperRuntime?.live_wrapper_telemetry || null;
  state.releaseWrapperReadiness = state.controlPanel.release_wrapper_readiness || null;
  if (releaseWrapperSessionLifecycle) {
    state.releaseWrapperSessionLifecycle = releaseWrapperSessionLifecycle;
  }
  if (releaseWrapperStatus) {
    state.releaseWrapperStatus = releaseWrapperStatus;
    state.autonomousUpdates = releaseWrapperStatus.autonomous_updates || state.autonomousUpdates;
    state.releaseWrapperRuntime = releaseWrapperStatus.runtime || state.releaseWrapperRuntime;
    state.releaseHarnessRuntime = releaseWrapperStatus.runtime || state.releaseHarnessRuntime;
    state.cluster9TeacherReconciliation = releaseWrapperStatus.cluster9_teacher_reconciliation
      || releaseWrapperStatus.runtime?.cluster9_teacher_reconciliation
      || state.cluster9TeacherReconciliation;
    state.releaseWrapperTelemetry = releaseWrapperStatus.runtime?.live_wrapper_telemetry || state.releaseWrapperTelemetry;
    state.releaseWrapperReadiness = releaseWrapperStatus.readiness || state.releaseWrapperReadiness;
  }
  state.blackBox = state.controlPanel.blackbox_recorder || null;
  state.hiveConsensus = state.controlPanel.hive_consensus_scorecard || null;
  state.aoHive = state.controlPanel.ao_hive_scorecard || null;
  state.expertsHive = state.controlPanel.experts_hive_scorecard || null;
  state.researcherSwarm = state.controlPanel.researcher_swarm_scorecard || null;
  state.forwardRadar = state.controlPanel.forward_radar_scorecard || null;
  state.evalSuite = state.controlPanel.eval_suite_scorecard || null;
  state.memoryProvenance = state.controlPanel.memory_provenance_scorecard || null;
  state.memoryQuality = state.controlPanel.memory_quality_scorecard || null;
  state.artifactTrust = state.controlPanel.artifact_trust_scorecard || null;
  state.hardwareMatrix = state.controlPanel.hardware_matrix_scorecard || null;
  state.visualOps = state.controlPanel.visualops_scorecard || null;
  state.toolExecution = state.controlPanel.tool_execution_scorecard || null;
  state.assimilationTargets = state.controlPanel.assimilation_target_scorecard || null;
  state.videoAssimilation = state.controlPanel.video_assimilation_scorecard || null;
  state.retrievalPlanner = state.controlPanel.retrieval_planner_scorecard || null;
  state.operatorEvents = state.controlPanel.operator_events_scorecard || null;
  state.conceptTelemetry = state.controlPanel.concept_telemetry_scorecard || null;
  state.hiveNeuralSubstrate = state.controlPanel.hive_neural_substrate_scorecard || null;
  state.sandboxAgentFactory = state.controlPanel.sandbox_agent_factory_scorecard || null;
  state.outputDelivery = state.controlPanel.output_delivery_scorecard || null;
  await loadHiveNeuralSubstrateScorecard(session);
  await loadSandboxAgentFactoryScorecard(session);
  const currentExists = (state.controlPanel.pages || []).some((page) => page.page_id === state.currentPageId);
  if (!currentExists) {
    state.currentPageId = (state.controlPanel.pages || [])[0]?.page_id || "overview";
  }
  renderAll();
  await loadSurfaceDrilldown();
  setConnection("connected", `Connected | ${state.controlPanel.page_count || 0} pages`);
}

async function loadReleaseWrapperStatusCard(session) {
  const url = `/ops/wrapper/status-card?session_id=${encodeURIComponent(session)}`;
  const card = await fetchJSON(url);
  state.releaseWrapperStatus = card;
  state.autonomousUpdates = card.autonomous_updates || state.autonomousUpdates;
  state.releaseWrapperRuntime = card.runtime || state.releaseWrapperRuntime;
  state.releaseHarnessRuntime = card.runtime || state.releaseHarnessRuntime;
  state.cluster9TeacherReconciliation = card.cluster9_teacher_reconciliation
    || card.runtime?.cluster9_teacher_reconciliation
    || state.cluster9TeacherReconciliation;
  state.releaseWrapperTelemetry = card.runtime?.live_wrapper_telemetry || state.releaseWrapperTelemetry;
  state.releaseWrapperReadiness = card.readiness || state.releaseWrapperReadiness;
  return card;
}

async function loadReleaseWrapperSessionLifecycle(session) {
  const url = `/ops/wrapper/session-lifecycle?session_id=${encodeURIComponent(session)}`;
  const lifecycle = await fetchJSON(url);
  state.releaseWrapperSessionLifecycle = lifecycle;
  state.releaseWrapperTelemetry = lifecycle.telemetry || state.releaseWrapperTelemetry;
  state.releaseWrapperReadiness = lifecycle.readiness || state.releaseWrapperReadiness;
  return lifecycle;
}

async function refreshReleaseWrapperStatusCard() {
  const session = dom.sessionInput.value || sessionId();
  const card = await loadReleaseWrapperStatusCard(session);
  await loadReleaseWrapperSessionLifecycle(session).catch(() => null);
  renderAutonomousUpdatesScorecard();
  return card;
}

function releaseWrapperAdminActionPayload(action, lane) {
  const default_sandbox_command = lane.default_sandbox_command || "pytest tests/test_release_wrapper_runtime.py::test_release_wrapper_status_card_is_lightweight_control_panel_surface_after_restart -q";
  const proposal = state.autonomousUpdates?.latest_dream_research_proposal
    || state.autonomousUpdates?.latest_release_health_repair_proposal
    || {};
  const sandboxEvidence = proposal.latest_sandbox_test_evidence || state.autonomousUpdates?.latest_sandbox_test_evidence || {};
  if (action === "admin_approval") {
    return {
      approved_by: "admin",
      approval_ref: "control-panel::release-wrapper-admin-action-lane",
    };
  }
  if (action === "sandbox_tests") {
    return {
      command: default_sandbox_command,
      timeout_seconds: 60,
    };
  }
  if (action === "apply") {
    return {
      test_refs: [default_sandbox_command],
      test_evidence_refs: sandboxEvidence.evidence_ref ? [sandboxEvidence.evidence_ref] : [],
    };
  }
  if (action === "rollback") {
    return { reason: "control-panel-release-wrapper-admin-action-lane" };
  }
  if (action === "run_release_readiness_evidence") {
    return {
      session_id: dom.sessionInput.value || sessionId(),
      command: default_sandbox_command,
      timeout_seconds: 60,
      approved_by: "control-panel",
      approval_ref: "control-panel::release-wrapper-readiness-runner",
    };
  }
  if (action === "run_boot_supervisor") {
    const location = window.location || {};
    return {
      session_id: dom.sessionInput.value || sessionId(),
      base_url: location.origin || "",
      host: location.hostname || "127.0.0.1",
      port: Number(location.port || 0),
      pid: 0,
      readiness_command: default_sandbox_command,
    };
  }
  if (action === "run_initial_release_supervisor") {
    const location = window.location || {};
    return {
      session_id: dom.sessionInput.value || sessionId(),
      base_url: location.origin || "",
      host: location.hostname || "127.0.0.1",
      port: Number(location.port || 0),
      pid: 0,
      readiness_command: default_sandbox_command,
      timeout_seconds: 60,
      approved_by: "control-panel",
      approval_ref: "control-panel::initial-release-supervisor",
    };
  }
  if (action === "run_release_product_smoke") {
    const location = window.location || {};
    return {
      session_id: dom.sessionInput.value || sessionId(),
      base_url: location.origin || "",
      host: location.hostname || "127.0.0.1",
      port: Number(location.port || 0),
      pid: 0,
      readiness_command: default_sandbox_command,
      timeout_seconds: 60,
      approved_by: "control-panel",
      approval_ref: "control-panel::release-product-smoke",
    };
  }
  if (action === "run_release_health_heartbeat_loop") {
    const location = window.location || {};
    return {
      session_id: dom.sessionInput.value || sessionId(),
      trigger: "control-panel",
      max_cycles: 3,
      interval_seconds: 30,
      max_retry_attempts: 3,
      retry_backoff_seconds: 2,
      base_url: location.origin || "",
      host: location.hostname || "127.0.0.1",
      port: Number(location.port || 0),
      pid: 0,
    };
  }
  if (action === "configure_release_health_heartbeat_supervisor") {
    return {
      session_id: dom.sessionInput.value || sessionId(),
      enabled: true,
      interval_seconds: 60,
      max_pulses_per_tick: 1,
      schedule_immediately: false,
      configured_by: "control-panel",
    };
  }
  if (action === "run_release_health_heartbeat_supervisor_repair") {
    return {
      session_id: dom.sessionInput.value || sessionId(),
      command: default_sandbox_command,
      timeout_seconds: 60,
      approved_by: "control-panel",
      approval_ref: "control-panel::heartbeat-supervisor-repair",
    };
  }
  return {};
}

async function runReleaseWrapperAdminAction(event) {
  const button = event.target.closest("[data-release-wrapper-action]");
  if (!button) {
    return;
  }
  const action = button.dataset.releaseWrapperAction || "";
  if (action === "refresh_status_card") {
    try {
      button.disabled = true;
      await refreshReleaseWrapperStatusCard();
      setConnection("connected", "Release Harness status refreshed");
    } catch (error) {
      setConnection("error", error.message);
    } finally {
      button.disabled = false;
    }
    return;
  }
  const lane = state.releaseWrapperStatus?.operator_action_lane || {};
  const refByAction = {
    admin_approval: "admin_approval_ref",
    sandbox_tests: "sandbox_tests_ref",
    apply: "apply_ref",
    rollback: "rollback_ref",
    run_release_readiness_evidence: "run_readiness_evidence_ref",
    run_boot_supervisor: "run_boot_supervisor_ref",
    run_initial_release_supervisor: "run_initial_release_supervisor_ref",
    run_release_product_smoke: "run_release_product_smoke_ref",
    run_release_health_heartbeat_loop: "run_release_health_heartbeat_loop_ref",
    configure_release_health_heartbeat_supervisor: "configure_release_health_heartbeat_supervisor_ref",
    run_release_health_heartbeat_supervisor_repair: "run_release_health_heartbeat_supervisor_repair_ref",
  };
  const endpoint = lane[refByAction[action]];
  if (!endpoint) {
    setConnection("error", `Release Harness action is unavailable: ${action || "unknown"}`);
    return;
  }
  try {
    button.disabled = true;
    setConnection("", `Running Release Harness ${pretty(action)}`);
    const payload = await fetchJSON(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(releaseWrapperAdminActionPayload(action, lane)),
    });
    state.releaseWrapperLastAction = payload;
    await refreshReleaseWrapperStatusCard();
    setConnection("connected", `Release Harness ${pretty(action)} recorded`);
  } catch (error) {
    setConnection("error", error.message);
  } finally {
    button.disabled = false;
  }
}

async function loadHiveNeuralSubstrateScorecard(session) {
  try {
    state.hiveNeuralSubstrate = await fetchJSON(
      `${canonScorecardEndpoints.hiveNeuralSubstrate}?session_id=${encodeURIComponent(session)}`
    );
  } catch {
    state.hiveNeuralSubstrate = state.hiveNeuralSubstrate || null;
  }
  try {
    state.hiveNeuralSubstrateReplay = await fetchJSON(
      `${canonScorecardEndpoints.hiveNeuralSubstrateReplay}?session_id=${encodeURIComponent(session)}`
    );
  } catch {
    state.hiveNeuralSubstrateReplay = state.hiveNeuralSubstrateReplay || null;
  }
}

async function loadSandboxAgentFactoryScorecard(session) {
  try {
    state.sandboxAgentFactory = await fetchJSON(
      `${canonScorecardEndpoints.sandboxAgentFactory}?session_id=${encodeURIComponent(session)}`
    );
  } catch {
    state.sandboxAgentFactory = state.sandboxAgentFactory || null;
  }
}

async function loadRuntimeAcceleration() {
  const payload = await fetchJSON("/api/runtime-packs/status");
  dom.runtimeAccelerationMode.value = payload.mode.requested_mode;
  const decision = payload.active_decision || {};
  dom.runtimeAccelerationStatus.textContent = decision.available
    ? `${decision.route_id} (${payload.status_label})`
    : `${payload.status_label}: ${(decision.reason_codes || []).join(", ")}`;
}

async function applyRuntimeAccelerationMode() {
  dom.runtimeAccelerationApply.disabled = true;
  try {
    await fetchJSON("/api/runtime-packs/mode", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode: dom.runtimeAccelerationMode.value }),
    });
    await loadRuntimeAcceleration();
  } catch (error) {
    dom.runtimeAccelerationStatus.textContent = error.message;
  } finally {
    dom.runtimeAccelerationApply.disabled = false;
  }
}

dom.sessionInput.value = sessionId();
dom.refreshButton.addEventListener("click", () => {
  loadControlPanel().catch((error) => {
    setConnection("error", error.message);
  });
});
dom.runtimeAccelerationApply.addEventListener("click", applyRuntimeAccelerationMode);
dom.sessionInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    localStorage.setItem("nn_session", dom.sessionInput.value || sessionId());
    loadControlPanel().catch((error) => setConnection("error", error.message));
  }
});
dom.canonCommandForm.addEventListener("submit", issueCanonCommand);
dom.realizeSurfaceButton.addEventListener("click", realizeSelectedSurface);
dom.canonProofForm.addEventListener("submit", recordAnswerProof);
dom.datasetRadarRefreshForm.addEventListener("submit", submitDatasetRadarRefresh);
dom.datasetRadarBatchButton.addEventListener("click", runDatasetRadarPresetBatch);
dom.datasetRadarCandidateReviewForm.addEventListener("submit", submitDatasetRadarCandidateReview);
dom.datasetRadarMaterialRequestForm.addEventListener("submit", submitDatasetRadarMaterialRequest);
dom.datasetRadarSourceDetailForm.addEventListener("submit", inspectDatasetRadarSourceDetail);
dom.datasetRadarScorecard.addEventListener("click", inspectDatasetRadarSourceFromButton);
dom.knowledgeArtifactsScorecard.addEventListener("click", scanLatestKnowledgeArtifactTrust);
dom.growthEngineScorecard.addEventListener("click", inspectLatestGrowthCycleReplay);
dom.autonomousUpdatesScorecard.addEventListener("click", runReleaseWrapperAdminAction);
dom.datasetForgeApplyHandoffButton.addEventListener("click", applyDatasetForgeHandoffTemplate);
dom.datasetForgeManifestForm.addEventListener("submit", submitDatasetForgeManifest);

loadControlPanel().catch((error) => {
  setConnection("error", error.message);
});
loadRuntimeAcceleration().catch((error) => {
  dom.runtimeAccelerationStatus.textContent = error.message;
});
