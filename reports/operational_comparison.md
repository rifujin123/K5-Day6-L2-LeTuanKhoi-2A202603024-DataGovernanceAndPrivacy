# So sánh vận hành baseline và PoC

Sinh bằng `python -m tools.report_t02_results`. Chưa có GT để so sánh chất lượng.

| Chỉ tiêu | Baseline | PoC |
|---|---:|---:|
| Ảnh được xếp hạng | 96 | 96 |
| Ảnh trong queue eval | 20 | 20 |
| Exit code | 0 | 0 |
| Runtime toàn pipeline (s) | 1.3647 | 2.0355 |
| Runtime / 100 ảnh (s) | 1.4216 | 2.1203 |
| Xử lý feature + score (ms/ảnh) | 7.682 | 14.721 |
| Quyết định queue | HOLD | HOLD |
| Defect Recall@20 | Chưa có GT | Chưa có GT |
| Precision@20 | Chưa có GT | Chưa có GT |

Top-20 giao nhau: 14/20; Jaccard: 0.5385.
Runtime là một lượt chạy cục bộ, chưa phải benchmark; thời gian review của người dùng chưa được đo.
