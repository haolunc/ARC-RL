# Recovery Analysis: `arc2_training_simple_qwen35`

Tasks that failed on the first attempt but succeeded on a later attempt.

## Summary

| Metric | Count |
|---|---|
| Total tasks | 998 |
| Solved on first attempt | 597 |
| Failed first, recovered later | 90 |
| Never solved | 312 |
| **Total solved** | **670** (67.1%) |

Recovery accounts for **13.4%** of all solved tasks (90 / 670).

## First-Attempt Failure Reasons (for recovered tasks)

| Reason | Count |
|---|---|
| wrong_output | 64 |
| shape_mismatch | 11 |
| runtime_error | 11 |
| test_fail (train passed, test failed) | 4 |

## Recovery Step Distribution

| Recovered at step | Count |
|---|---|
| 2 | 37 |
| 3 | 29 |
| 4 | 15 |
| 5 | 9 |

## Recovered Task List

| task_id | first_fail_reason | success_step | total_steps |
|---|---|---|---|
| 025d127b | wrong_output | 2 | 2 |
| 0a2355a6 | runtime_error | 2 | 2 |
| 0a938d79 | wrong_output | 3 | 3 |
| 1478ab18 | runtime_error | 4 | 4 |
| 14b8e18c | wrong_output | 3 | 3 |
| 17b80ad2 | wrong_output | 4 | 4 |
| 17b866bd | wrong_output | 4 | 5 |
| 18286ef8 | wrong_output | 2 | 2 |
| 182e5d0f | wrong_output | 3 | 3 |
| 1990f7a8 | runtime_error | 4 | 4 |
| 1c02dbbe | wrong_output | 5 | 5 |
| 1c0d0a4b | wrong_output | 3 | 3 |
| 1d398264 | wrong_output | 3 | 3 |
| 21f83797 | wrong_output | 2 | 2 |
| 22806e14 | wrong_output | 2 | 2 |
| 228f6490 | runtime_error | 3 | 3 |
| 239be575 | wrong_output | 4 | 4 |
| 25c199f5 | shape_mismatch | 2 | 3 |
| 278e5215 | shape_mismatch | 2 | 2 |
| 2bee17df | wrong_output | 2 | 2 |
| 2de01db2 | wrong_output | 5 | 5 |
| 36d67576 | wrong_output | 3 | 3 |
| 37d3e8b2 | wrong_output | 4 | 4 |
| 3e980e27 | wrong_output | 4 | 4 |
| 3f7978a0 | shape_mismatch | 2 | 2 |
| 41ace6b5 | wrong_output | 3 | 3 |
| 470c91de | wrong_output | 5 | 5 |
| 4c177718 | shape_mismatch | 4 | 5 |
| 5034a0b5 | wrong_output | 3 | 3 |
| 52df9849 | test_fail | 2 | 5 |
| 53b68214 | wrong_output | 2 | 2 |
| 55059096 | wrong_output | 4 | 4 |
| 56dc2b01 | wrong_output | 2 | 2 |
| 5833af48 | runtime_error | 2 | 2 |
| 5ffb2104 | runtime_error | 2 | 2 |
| 62b74c02 | shape_mismatch | 2 | 2 |
| 662c240a | test_fail | 5 | 5 |
| 67c52801 | wrong_output | 3 | 3 |
| 689c358e | wrong_output | 3 | 3 |
| 6c434453 | wrong_output | 2 | 2 |
| 6cdd2623 | wrong_output | 2 | 2 |
| 6cf79266 | wrong_output | 3 | 3 |
| 72a961c9 | wrong_output | 5 | 5 |
| 72ca375d | shape_mismatch | 2 | 2 |
| 73c3b0d8 | wrong_output | 2 | 2 |
| 7acdf6d3 | wrong_output | 4 | 4 |
| 7d18a6fb | shape_mismatch | 3 | 3 |
| 7e2bad24 | wrong_output | 2 | 5 |
| 7f4411dc | wrong_output | 3 | 3 |
| 80af3007 | wrong_output | 3 | 3 |
| 81c0276b | shape_mismatch | 2 | 2 |
| 85b81ff1 | wrong_output | 3 | 3 |
| 880c1354 | wrong_output | 5 | 5 |
| 8a371977 | wrong_output | 2 | 2 |
| 8d5021e8 | wrong_output | 2 | 2 |
| 9720b24f | wrong_output | 3 | 3 |
| 98cf29f8 | wrong_output | 2 | 2 |
| 992798f6 | wrong_output | 3 | 3 |
| 9968a131 | runtime_error | 2 | 2 |
| 9b4c17c4 | wrong_output | 3 | 3 |
| 9c1e755f | runtime_error | 2 | 2 |
| 9def23fe | wrong_output | 2 | 2 |
| 9f41bd9c | test_fail | 5 | 5 |
| 9f669b64 | wrong_output | 3 | 3 |
| a2d730bd | runtime_error | 4 | 4 |
| a699fb00 | test_fail | 2 | 2 |
| a87f7484 | wrong_output | 2 | 2 |
| aa300dc3 | wrong_output | 2 | 2 |
| abbfd121 | shape_mismatch | 2 | 2 |
| ac3e2b04 | wrong_output | 3 | 3 |
| af726779 | wrong_output | 2 | 2 |
| b745798f | wrong_output | 4 | 4 |
| ba9d41b8 | wrong_output | 3 | 3 |
| bb52a14b | wrong_output | 3 | 3 |
| beb8660c | wrong_output | 2 | 2 |
| c1990cce | wrong_output | 2 | 2 |
| c62e2108 | wrong_output | 3 | 3 |
| cdecee7f | shape_mismatch | 2 | 2 |
| ce8d95cc | shape_mismatch | 3 | 3 |
| d5c634a2 | wrong_output | 5 | 5 |
| e21a174a | wrong_output | 4 | 4 |
| e619ca6e | runtime_error | 3 | 3 |
| ecdecbb3 | wrong_output | 5 | 5 |
| f18ec8cc | wrong_output | 3 | 3 |
| f21745ec | wrong_output | 3 | 3 |
| f28a3cbb | wrong_output | 3 | 3 |
| f823c43c | wrong_output | 4 | 4 |
| f8ff0b80 | runtime_error | 2 | 2 |
| feca6190 | wrong_output | 2 | 2 |
| ff2825db | wrong_output | 4 | 4 |
