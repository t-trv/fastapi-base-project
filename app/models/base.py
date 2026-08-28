from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base Class của SQLAlchemy 2.0.
    Chỉ tự động định nghĩa hàm __repr__ để in thông tin Model dễ đọc và bảo mật.
    """

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        # Lấy danh sách tên các cột thực tế của bảng (loại bỏ tự động các relationships)
        columns = self.__table__.columns.keys()

        attrs = []
        for key in columns:
            if key in self.__dict__:
                # Ẩn các trường nhạy cảm để bảo mật thông tin trong log
                if any(sec in key.lower() for sec in ["password", "token", "secret"]):
                    continue
                attrs.append(f"    {key}={self.__dict__[key]!r}")

        if attrs:
            return f"{class_name}(\n" + ",\n".join(attrs) + "\n)"
        return f"{class_name}()"
