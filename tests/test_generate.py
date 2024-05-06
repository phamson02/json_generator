from legal_queries_generator import generate_batch, Content


def mock_bad_generator(texts: list[str]) -> list[str]:
    return ["Bad"] * len(texts)


def mock_good_generator(texts: list[str]) -> list[str]:
    return [
        '{"aspects": ["Khen thưởng cho những cá nhân có thành tích trong công tác bảo vệ sức khỏe nhân dân", "Xử lý các hành vi vi phạm về bảo vệ sức khỏe nhân dân"], "questions": ["Luật Bảo vệ sức khỏe nhân dân quy định những hình thức khen thưởng nào dành cho những cá nhân có thành tích trong công tác bảo vệ sức khỏe nhân dân?", "Pháp luật quy định những hình thức xử lý như thế nào đối với những hành vi vi phạm về bảo vệ sức khỏe nhân dân?"]}'
    ] * len(texts)


def mock_somewhat_bad_generator(texts: list[str]) -> list[str]:
    return ["Bad"] * (len(texts) - 1) + [
        '{"aspects": ["Khen thưởng cho những cá nhân có thành tích trong công tác bảo vệ sức khỏe nhân dân", "Xử lý các hành vi vi phạm về bảo vệ sức khỏe nhân dân"], "questions": ["Luật Bảo vệ sức khỏe nhân dân quy định những hình thức khen thưởng nào dành cho những cá nhân có thành tích trong công tác bảo vệ sức khỏe nhân dân?", "Pháp luật quy định những hình thức xử lý như thế nào đối với những hành vi vi phạm về bảo vệ sức khỏe nhân dân?"]}'
    ]


def test_bad_generate():
    contents = [
        Content(
            domain="CIVIL",
            metadata="Bộ luật dân sự 2015",
            grounded_content="Người có nghĩa vụ trả tiền thuê nhà phải trả tiền thuê đúng hạn, trừ trường hợp có thoả thuận khác.",
        ),
        Content(
            domain="CIVIL",
            metadata="Bộ luật dân sự 2015",
            grounded_content="Người có nghĩa vụ trả tiền thuê nhà phải trả tiền thuê đúng hạn, trừ trường hợp có thoả thuận khác.",
        ),
    ]

    aspects, questions = generate_batch(contents, mock_bad_generator)

    assert aspects == [[], []]
    assert questions == [[], []]


def test_good_generate():
    contents = [
        Content(
            domain="CIVIL",
            metadata="Bộ luật dân sự 2015",
            grounded_content="Người có nghĩa vụ trả tiền thuê nhà phải trả tiền thuê đúng hạn, trừ trường hợp có thoả thuận khác.",
        ),
        Content(
            domain="CIVIL",
            metadata="Bộ luật dân sự 2015",
            grounded_content="Người có nghĩa vụ trả tiền thuê nhà phải trả tiền thuê đúng hạn, trừ trường hợp có thoả thuận khác.",
        ),
    ]

    aspects, questions = generate_batch(contents, mock_good_generator)

    assert aspects == [
        [
            "Khen thưởng cho những cá nhân có thành tích trong công tác bảo vệ sức khỏe nhân dân",
            "Xử lý các hành vi vi phạm về bảo vệ sức khỏe nhân dân",
        ],
        [
            "Khen thưởng cho những cá nhân có thành tích trong công tác bảo vệ sức khỏe nhân dân",
            "Xử lý các hành vi vi phạm về bảo vệ sức khỏe nhân dân",
        ],
    ]
    assert questions == [
        [
            "Luật Bảo vệ sức khỏe nhân dân quy định những hình thức khen thưởng nào dành cho những cá nhân có thành tích trong công tác bảo vệ sức khỏe nhân dân?",
            "Pháp luật quy định những hình thức xử lý như thế nào đối với những hành vi vi phạm về bảo vệ sức khỏe nhân dân?",
        ],
        [
            "Luật Bảo vệ sức khỏe nhân dân quy định những hình thức khen thưởng nào dành cho những cá nhân có thành tích trong công tác bảo vệ sức khỏe nhân dân?",
            "Pháp luật quy định những hình thức xử lý như thế nào đối với những hành vi vi phạm về bảo vệ sức khỏe nhân dân?",
        ],
    ]


def test_somewhat_bad_generate():
    contents = [
        Content(
            domain="CIVIL",
            metadata="Bộ luật dân sự 2015",
            grounded_content="Người có nghĩa vụ trả tiền thuê nhà phải trả tiền thuê đúng hạn, trừ trường hợp có thoả thuận khác.",
        ),
        Content(
            domain="CIVIL",
            metadata="Bộ luật dân sự 2015",
            grounded_content="Người có nghĩa vụ trả tiền thuê nhà phải trả tiền thuê đúng hạn, trừ trường hợp có thoả thuận khác.",
        ),
    ]

    aspects, questions = generate_batch(contents, mock_somewhat_bad_generator)

    assert aspects == [
        [
            "Khen thưởng cho những cá nhân có thành tích trong công tác bảo vệ sức khỏe nhân dân",
            "Xử lý các hành vi vi phạm về bảo vệ sức khỏe nhân dân",
        ],
        [
            "Khen thưởng cho những cá nhân có thành tích trong công tác bảo vệ sức khỏe nhân dân",
            "Xử lý các hành vi vi phạm về bảo vệ sức khỏe nhân dân",
        ],
    ]
    assert questions == [
        [
            "Luật Bảo vệ sức khỏe nhân dân quy định những hình thức khen thưởng nào dành cho những cá nhân có thành tích trong công tác bảo vệ sức khỏe nhân dân?",
            "Pháp luật quy định những hình thức xử lý như thế nào đối với những hành vi vi phạm về bảo vệ sức khỏe nhân dân?",
        ],
        [
            "Luật Bảo vệ sức khỏe nhân dân quy định những hình thức khen thưởng nào dành cho những cá nhân có thành tích trong công tác bảo vệ sức khỏe nhân dân?",
            "Pháp luật quy định những hình thức xử lý như thế nào đối với những hành vi vi phạm về bảo vệ sức khỏe nhân dân?",
        ],
    ]
