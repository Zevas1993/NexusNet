# AndroidWorld Mobile Agent Spec

Status: P1 online assimilation target. Research-only until emulator setup and license are verified.

## Source Evidence

- AndroidWorld paper: https://arxiv.org/abs/2405.14573
- AndroidWorld repository: https://github.com/google-research/android_world
- Source status: primary paper page and public benchmark repository.

## Finding

AndroidWorld provides a live Android emulator environment with 116 programmatic tasks across 20 Android apps. Tasks are dynamically parameterized and include initialization, success-checking, and tear-down logic over real device state.

## NexusNet Assimilation Target

Use AndroidWorld as the mobile VisualOps certification pattern. NexusNet should distinguish desktop browser automation from mobile app control, because mobile state, accessibility trees, app permissions, and parameterized tasks introduce different failure modes.

## Proposed NexusNet Components

- `MobileTaskFixture`: app, parameter seed, initial state, success checker, tear-down action, and permission scope.
- `AndroidActionTrace`: observation source, tap/text/action, app state delta, and screenshot/artifact reference.
- `MobileCapabilityPassport`: emulator/device profile, installed apps, accessibility bridge, and allowed action classes.
- `MobileVisualOpsGate`: prevents live-device actions until emulator certification passes.

## Promotion Gates

- Start on emulator-only tasks.
- Require deterministic success checks and reset logic.
- Keep user phone/device actions opt-in and separate from benchmark automation.
- Track app permissions as authority, not mere environment metadata.

## Risks

- Android emulator setup can be fragile and hardware-dependent.
- Accessibility observations can drift across app versions and OS versions.
- Mobile UI automation may need stricter privacy gates than desktop browser tasks.
