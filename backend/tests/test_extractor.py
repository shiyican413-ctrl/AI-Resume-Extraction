from app.services.extractor import merge_extract_result


def test_merge_extract_result_formats_education_as_chinese_text():
    base = {
        "basic_info": {},
        "job_intention": {},
        "background": {
            "years_of_experience": "",
            "education": "",
            "projects": [],
        },
        "skills": [],
    }
    ai_result = {
        "background": {
            "education": [
                {
                    "degree": "本科",
                    "school": "厦门大学嘉庚学院",
                    "period": "2024.09 - 2027.09",
                    "major_courses": ["数据结构与算法", "计算机网络", "操作系统"],
                }
            ]
        }
    }

    result = merge_extract_result(base, ai_result)

    assert result["background"]["education"] == (
        "本科，厦门大学嘉庚学院，2024.09 - 2027.09，"
        "主修：数据结构与算法、计算机网络、操作系统"
    )


def test_merge_extract_result_uses_ai_summary_when_available():
    base = {
        "basic_info": {"name": "张三"},
        "job_intention": {"position": "后端开发"},
        "background": {
            "years_of_experience": "2年",
            "education": "本科",
            "projects": [],
        },
        "skills": ["Python", "FastAPI"],
    }
    ai_result = {"summary": "候选人具备后端开发基础，熟悉 Python 和 FastAPI。"}

    result = merge_extract_result(base, ai_result)

    assert result["summary"] == "候选人具备后端开发基础，熟悉 Python 和 FastAPI。"


def test_merge_extract_result_builds_fallback_summary_without_ai():
    base = {
        "basic_info": {"name": "李四"},
        "job_intention": {"position": "Java 开发"},
        "background": {
            "years_of_experience": "3年",
            "education": "本科",
            "projects": [],
        },
        "skills": ["Java", "MySQL", "Redis"],
    }

    result = merge_extract_result(base, None)

    assert result["summary"] == "李四的求职方向为Java 开发，学历背景为本科，工作年限为3年，主要技能包括Java、MySQL、Redis。"
