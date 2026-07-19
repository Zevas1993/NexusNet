"""Vendor-neutral accelerator-pack contracts and process isolation.

Exports are resolved lazily so an isolated worker can import its protocol and
kernel without loading coordinator-only HTTP, registry, or vendor dependencies.
"""

from __future__ import annotations

from importlib import import_module


_LAZY_EXPORTS = {
    "AcquiredArtifact": (".acquisition", "AcquiredArtifact"),
    "AcquisitionError": (".acquisition", "AcquisitionError"),
    "AcquisitionPolicy": (".acquisition", "AcquisitionPolicy"),
    "ArtifactAcquirer": (".acquisition", "ArtifactAcquirer"),
    "BuiltInPackCatalog": (".catalog", "BuiltInPackCatalog"),
    "CalibrationKey": (".calibration", "CalibrationKey"),
    "CalibrationLedger": (".calibration", "CalibrationLedger"),
    "CalibrationRecord": (".calibration", "CalibrationRecord"),
    "CompatibilityDecision": (".compatibility", "CompatibilityDecision"),
    "EnvironmentBuildError": (".installer", "EnvironmentBuildError"),
    "ExecutionMode": (".contracts", "ExecutionMode"),
    "JsonLineCodec": (".protocol", "JsonLineCodec"),
    "LockedWheel": (".environment_locks", "LockedWheel"),
    "ModelFormat": (".contracts", "ModelFormat"),
    "PackCandidate": (".catalog", "PackCandidate"),
    "PackCircuitBreaker": (".lifecycle", "PackCircuitBreaker"),
    "PackCompatibilityEvaluator": (".compatibility", "PackCompatibilityEvaluator"),
    "PackInstallError": (".installer", "PackInstallError"),
    "PackInstaller": (".installer", "PackInstaller"),
    "PackLifecycleState": (".contracts", "PackLifecycleState"),
    "PackLifecycleManager": (".lifecycle", "PackLifecycleManager"),
    "PackType": (".contracts", "PackType"),
    "PackVerification": (".installer", "PackVerification"),
    "PrivateEnvironmentBuilder": (".installer", "PrivateEnvironmentBuilder"),
    "ProvenanceSummary": (".lifecycle", "ProvenanceSummary"),
    "ProtocolError": (".protocol", "ProtocolError"),
    "RegistryError": (".registry", "RegistryError"),
    "RouteDecision": (".route_selection", "RouteDecision"),
    "RouteEvidence": (".route_selection", "RouteEvidence"),
    "RouteRequest": (".route_selection", "RouteRequest"),
    "RouteUnavailableError": (".route_selection", "RouteUnavailableError"),
    "RuntimeModeStore": (".route_selection", "RuntimeModeStore"),
    "RuntimePackManifest": (".contracts", "RuntimePackManifest"),
    "RuntimePackRecord": (".registry", "RuntimePackRecord"),
    "RuntimePackRegistry": (".registry", "RuntimePackRegistry"),
    "SbomSummary": (".lifecycle", "SbomSummary"),
    "VendorPackCandidate": (".vendor_packs", "VendorPackCandidate"),
    "VendorPackCatalog": (".vendor_packs", "VendorPackCatalog"),
    "VendorSupportRecord": (".vendor_packs", "VendorSupportRecord"),
    "VerifiedRouteSelector": (".route_selection", "VerifiedRouteSelector"),
    "WindowsMlCatalog": (".windows_ml", "WindowsMlCatalog"),
    "WindowsMlDiscovery": (".windows_ml", "WindowsMlDiscovery"),
    "WindowsMlProviderDecision": (".windows_ml", "WindowsMlProviderDecision"),
    "WindowsMlProviderObservation": (".windows_ml", "WindowsMlProviderObservation"),
    "WorkerAdapterFactory": (".worker_factory", "WorkerAdapterFactory"),
    "WorkerEnvironmentLock": (".environment_locks", "WorkerEnvironmentLock"),
    "WorkerFactoryError": (".worker_factory", "WorkerFactoryError"),
    "WorkerFrame": (".protocol", "WorkerFrame"),
    "WorkerOperation": (".protocol", "WorkerOperation"),
    "WorkerRequest": (".protocol", "WorkerRequest"),
    "WorkerSupervisor": (".supervisor", "WorkerSupervisor"),
    "WorkerSupervisorError": (".supervisor", "WorkerSupervisorError"),
    "WorkloadKind": (".contracts", "WorkloadKind"),
    "built_in_environment_locks": (".environment_locks", "built_in_environment_locks"),
    "environment_lock_for": (".environment_locks", "environment_lock_for"),
    "LifecycleReceipt": (".lifecycle", "LifecycleReceipt"),
}

__all__ = list(_LAZY_EXPORTS)


def __getattr__(name: str):
    target = _LAZY_EXPORTS.get(name)
    if target is None:
        raise AttributeError(name)
    module_name, attribute_name = target
    value = getattr(import_module(module_name, __name__), attribute_name)
    globals()[name] = value
    return value
