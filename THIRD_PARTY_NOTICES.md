# Third-party skill notices

Security Audit includes an explicitly reviewed local Windows compatibility overlay.
The original base and replacement hashes are recorded separately; its MIT license
is retained. See [patch provenance](patches/security-audit/README.md).

Unmodified imports retain their upstream contents; reviewed local changes are identified above and in the provenance lock. All upstream copyrights and MIT or Apache-2.0 licenses remain in the installed third-party skill directories. This notice does not relicense the five original user-authored skills or historical evaluation documents.

| Source | Included scope | License |
| --- | --- | --- |
| [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) | All 12 user skill directories on the tracked `latest` distribution branch | [MIT, Thompson Labs LLC](third_party/text-to-cad/LICENSE) |
| [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | All 6 user skill directories, plus the gain card's README/benchmark sources | [MIT, DietrichGebert](third_party/ponytail/LICENSE) |
| [wheresryan22/anatomy](https://github.com/wheresryan22/anatomy) | Full repository-root skill, kit, scripts, references, eight examples and upstream metadata | [MIT, Ryan](third_party/anatomy/LICENSE) |
| [morluto/rea](https://github.com/morluto/rea) | `reverse-engineer-anything` and its full reference directory | [MIT, morluto](third_party/rea/LICENSE) |
| [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | All 1 approved skill packages, including every support file | [MIT](third_party/taste/LICENSE) |
| [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) | All 1 approved skill packages, including every support file | [MIT](third_party/ppt-master/LICENSE) |
| [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | All 8 approved skill packages, including every support file | [Apache-2.0](third_party/hyperframes/LICENSE) |
| [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | All 1 approved skill packages, including every support file | [Apache-2.0](third_party/impeccable/LICENSE) |
| [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) | All 1 approved skill packages, including every support file | [MIT](third_party/security-audit/LICENSE) |

Exact commits, paths, Git-verified content hashes and license hashes are recorded in [the provenance lock](third_party/upstream-lock.json). Upstream READMEs are preserved under `third_party/<source>/README.md`; they describe the original products and are not evidence that their runtimes/plugins have been installed here.

CAD engines, analysis providers, runtime packages, fabrication services and any other separately acquired components have their own terms and licenses. They are not downloaded, bundled, registered or executed by the skills-only installer. Do not assume that the MIT skill license grants a commercial tool license or a third-party service account.
