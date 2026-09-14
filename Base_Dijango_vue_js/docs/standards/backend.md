# Chuẩn phát triển backend

## 1. Kiến trúc

Backend là modular monolith. Mỗi nghiệp vụ nằm trong `Base_dijango/apps/<module>`; giữ tên `views` theo
Django, không thêm `controllers` song song và không tạo repository chỉ bọc ORM.

- `api/views.py`: HTTP, authentication/permission, gọi serializer/service/selector và tạo response.
- `api/serializers.py`: input validation và output representation ở biên API.
- `services.py`: nghiệp vụ và thao tác ghi. Mặc định dùng function khi không có state.
- `selectors.py`: truy vấn đọc phức tạp hoặc tái sử dụng; truy vấn đơn giản không bắt buộc bọc.
- `models.py`: schema, quan hệ và invariant phù hợp; manager/queryset cho hành vi truy vấn gắn model.
- DTO/enum đặt trong module sở hữu; `common` chỉ chứa hạ tầng dùng chung thật sự.

Service không nhận `HttpRequest`/serializer. Selector không có side effect ghi. Không đặt nghiệp vụ quan
trọng chỉ trong serializer và không dùng signal cho luồng chính khi gọi service rõ hơn. Public service,
selector/helper có type hints; Python theo PEP 8, tên service/selector là động từ `snake_case` như
`update_profile`, `get_active_user_by_id`. Không tạo `BaseService` hay kế thừa nhiều tầng thiếu nhu cầu.

Luồng ghi chuẩn:

```python
class ProfileView(APIView):
    def patch(self, request):
        serializer = UpdateProfileInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = update_profile(user=request.user, **serializer.validated_data)
        return Response(UserOutputSerializer(user).data)
```

Service nhận dữ liệu rõ ràng, bảo vệ transaction khi cần và trả model/kết quả; view serialize output.

## 2. Serializer, DTO và enum

- Khai báo fields tường minh; không dùng `fields = "__all__"` cho API nghiệp vụ.
- Tách input/output khi dữ liệu hoặc trách nhiệm khác nhau. Password `write_only`; system field `read_only`.
- DRF mặc định bỏ qua field không khai báo bằng lỗi validation; không âm thầm chuyển field ngoài allowlist.
- PATCH phải dùng serializer phù hợp, xác định partial behavior và có test các field được/không được đổi.
- Dùng `dataclass` khi cấu trúc nội bộ đủ phức tạp; không tạo DTO giống hệt serializer và DTO không query DB.
  Chỉ `frozen=True` nếu use case cần bất biến.
- Model choices dùng `TextChoices`/`IntegerChoices`; logic nội bộ có thể dùng Python `Enum`. Enum nằm ở
  module sở hữu, tránh magic string và không trùng Groups/Permissions khi chưa có nhu cầu.
- Choices không thay database constraint cho invariant quan trọng.

`fields = "__all__"` hiện chỉ có trong cấu hình Django admin, không phải API serializer, nên là ngoại lệ
hợp lệ ngoài phạm vi hợp đồng API.

## 3. Database và migration

- Model change phải có migration cùng commit; không sửa/xóa migration đã chạy ở môi trường dùng chung.
- Không sửa schema thủ công. Data migration dùng historical models từ `apps.get_model`.
- Field bắt buộc trên bảng có dữ liệu cần kế hoạch nullable/default → backfill → constraint.
- Dùng database constraint cho uniqueness/invariant quan trọng và kiểm tra index có sẵn trước khi thêm.
- `transaction.atomic` cho thao tác nhiều bước phải nguyên tử, không bọc mọi function máy móc.
- Tránh N+1 dựa trên query thực tế; dùng `select_related`/`prefetch_related` có mục đích.
- Chỉ dùng raw SQL khi ORM không diễn đạt rõ; luôn parameterize.
- Migration chạy một lần ở deployment/release job, không chạy trong từng worker.
- Migration khó đảo ngược phải ghi chiến lược rollback/forward fix trong PR hoặc quyết định kiến trúc.

## 4. Security, lỗi và logging

Giữ JWT/CSRF/cookie hiện hành trừ khi nhiệm vụ cho phép đổi hợp đồng. Không hardcode secret, không log
password/token/Cookie/Authorization. Không nuốt lỗi hoặc trả thành công giả. Exception API đi qua
`common.exceptions.api_exception_handler`; lỗi server log cùng request ID nhưng response không lộ chi tiết.

## 5. Testing và quality gate

Test hành vi HTTP, permission, service, constraint và migration quan trọng; không mock toàn bộ ORM/auth
trong integration test và không dùng database/credential production. Bug nên có regression test. Auth,
permission, migration và API contract đổi phải có test tương ứng.

Ruff kiểm tra lint/format; Django checks và `makemigrations --check` kiểm tra cấu hình/schema; pytest kiểm
tra hành vi; drf-spectacular validate OpenAPI. Ranh giới trách nhiệm, query efficiency, transaction và
chất lượng migration vẫn cần review.

