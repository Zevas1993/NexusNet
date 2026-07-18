"""Vendor-neutral accelerator-pack contracts and process isolation."""

from .acquisition import AcquisitionError, AcquisitionPolicy, AcquiredArtifact, ArtifactAcquirer
from .catalog import BuiltInPackCatalog, PackCandidate
from .compatibility import CompatibilityDecision, PackCompatibilityEvaluator
from .contracts import (
    ExecutionMode,
    ModelFormat,
    PackLifecycleState,
    PackType,
    RuntimePackManifest,
    WorkloadKind,
)
from .protocol import JsonLineCodec, ProtocolError, WorkerFrame, WorkerOperation, WorkerRequest
from .installer import (
    EnvironmentBuildError,
    PackInstallError,
    PackInstaller,
    PackVerification,
    PrivateEnvironmentBuilder,
)
from .registry import RegistryError, RuntimePackRecord, RuntimePackRegistry
from .route_selection import (
    RouteDecision,
    RouteEvidence,
    RouteRequest,
    RouteUnavailableError,
    RuntimeModeStore,
    VerifiedRouteSelector,
)
from .supervisor import WorkerSupervisor, WorkerSupervisorError
from .worker_factory import WorkerAdapterFactory, WorkerFactoryError

__all__ = [
    "AcquiredArtifact",
    "AcquisitionError",
    "AcquisitionPolicy",
    "ArtifactAcquirer",
    "BuiltInPackCatalog",
    "CompatibilityDecision",
    "ExecutionMode",
    "EnvironmentBuildError",
    "JsonLineCodec",
    "ModelFormat",
    "PackCompatibilityEvaluator",
    "PackInstallError",
    "PackInstaller",
    "PackCandidate",
    "PackVerification",
    "PackLifecycleState",
    "PackType",
    "ProtocolError",
    "PrivateEnvironmentBuilder",
    "RegistryError",
    "RouteDecision",
    "RouteEvidence",
    "RouteRequest",
    "RouteUnavailableError",
    "RuntimePackManifest",
    "RuntimePackRecord",
    "RuntimePackRegistry",
    "RuntimeModeStore",
    "WorkerFrame",
    "WorkerAdapterFactory",
    "WorkerFactoryError",
    "WorkerOperation",
    "WorkerRequest",
    "WorkerSupervisor",
    "WorkerSupervisorError",
    "WorkloadKind",
    "VerifiedRouteSelector",
]
