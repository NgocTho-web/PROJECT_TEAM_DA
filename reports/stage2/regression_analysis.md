# Regression Analysis - Du doan gia sach (gbpprice)

## 1. Thiet lap
- Target: `gbpprice` (GBP, lien tuc). Chi dung 11623 dong sach UK; 510 dong sach tieng Viet co gia VND bi tron vao cung cot nen bi loai.
- Chia train/test 80/20 (`random_state=42`): 9298 / 2325 dong.
- Gia lech phai manh nen model hoc tren `log1p(gia)` va chuyen nguoc ve GBP khi du doan.
- Feature so: no_of_pages, height, width, spine, weight, salesRank, discount, pub_year, has_subtitle, has_edition, short_blurb_len, long_blurb_len, has_review.
- Feature phan loai (One-Hot): type, category, language, published_country, publisher_top.
- Da loai: isbn, link, name, author, cac cot rat dai (chi lay do dai), cac cot tieng Viet/VND (hang so cho sach UK), `isSecondHand` (hang so).

## 2. Ket qua tren tap test
| Model                 |     MSE |    RMSE |    MAE |     R2 |   R2_log |   R2_train |
|:----------------------|--------:|--------:|-------:|-------:|---------:|-----------:|
| LinearRegression      | 144.316 | 12.0132 | 4.9087 | 0.4259 |   0.687  |     0.2974 |
| DecisionTreeRegressor | 118.141 | 10.8693 | 5.1172 | 0.5301 |   0.6328 |     0.538  |

Baseline (luon du doan gia trung binh): RMSE = 15.867 GBP.

## 3. Model tot nhat
**DecisionTreeRegressor** (RMSE thap nhat).

## 4. Phan tich sai so
- Top feature quan trong (Decision Tree): num__weight, num__discount, cat__category_politics, num__no_of_pages, num__height.
- Ti le du doan thap hon thuc te: 45.9% (residual > 0).
- Xem `residual_plot.png`: neu residual tang theo gia du doan thi mo hinh sai so co he thong o nhom sach dat (artanddesign, hardback...). 
- Cac feature vat ly (kich thuoc, trong luong) va salesRank gan nhu khong tuong quan truc tiep voi gia, nen R2 bi gioi han.

## 5. Ban giao cho M5
- File: `models/regression/best_regression_model.joblib` (pipeline gom preprocessing + model, goi `.predict(DataFrame)` ra gia GBP).
- Dung `build_features()` trong `src/regression/train_regression.py` de tao DataFrame dau vao tu du lieu tho; chi tiet cot nam trong `regression_meta.json`.
