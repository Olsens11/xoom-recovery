# Exact v0.16.4-SPLITMODE-QA package and build provenance

**Candidate immutable and OFFLINE-VALIDATED, not hardware installed or trusted by currently flashed v6J-C.** Raw ZIP, full test audit, and original source are preserved privately on the Pi; public GitHub contains reviewed source and metadata, not an unreviewed binary bundle.

- Filename: `XoomToolkit-Desktop-Commander-0.16.4-SPLITMODE-QA.zip`; size 669,650 bytes.
- Outer SHA-256: `9cc600e87453ab2658e7b9c7e454ce9a738b8ebbaf4aa2d5c395b69cb2bf9e35`.
- Inner tar.xz SHA-256: `4e374129f32b9df7d7e11cd176015f5a151974d97b36865fee8ab11b40ca303e`; 27 regular members.
- Control SHA `ad69de67b25b153c0ff335cef7e54533df7c82d455132075171193847a0cae66` introduces the safe root:shell mode0750 /tmp/n24 owner/group checks for UID2000 workers on fresh extraction and reuse.
- QR wrapper SHA `313e424b323e52fc009538a95655b9d10a936ebfc0c224e5cc660f9bc07c4f56`, retained original core SHA `6177b01513698b59eb4fe9ff6782fee59917bfaf57cb7de24b63720e0d989c7e`, JITless QR helper SHA `53368329be7e51aa7f78d16ed9cbcdcd70344519d16158cdd86e2f069df71dab`.
- Unchanged: agent cloud bundle, main normal-JIT launcher, existing UID2000 filesystem tools, root policy modules, original updater and all unrelated packages.
- Source builder: [build_dc_v0164_splitmode_pin.py](build_dc_v0164_splitmode_pin.py); coordinated independent [31-gate verification](../../../../../recovery/versions/R22NEXT-V6K/R22NEXT-V6K-DC0164-PINNED-OFFLINE-DO-NOT-FLASH/independent_dc0164_v6k_qa.py).

**Image dependency:** the new [v6K recovery image](../../../../../recovery/versions/R22NEXT-V6K/DIRECTORY.md) pins this precise filename and both hashes. It has NOT been flashed. The existing v6J-C verifier still trusts only v0.16.3. No bypass or generic TWRP Install should be used.

[Coordinated dated QA and next hardware gates](../../../../../recovery/2026-10-19-V6K-DC0164-COORDINATED-VERIFIED-PINS-OFFLINE-QA.md) · [Parent](../DIRECTORY.md).
