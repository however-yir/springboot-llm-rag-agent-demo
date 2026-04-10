# ReAct Execution Trace Example

Question: `请帮我看下下周课程，并生成学习周报`

1. Thought: 我需要先获取课表，再生成周报。
2. Action: `get_course_schedule`
3. Observation: `Mon Data Structures / Wed Software Engineering / Fri Machine Learning`
4. Thought: 已获得课表，接下来生成周报摘要。
5. Action: `generate_weekly_report`
6. Observation: `summary + next_week_focus`
7. Final Answer: 结合课表与目标，给出可执行周计划。

对应接口返回可在 `trace` 字段中看到完整 `Thought -> Action -> Observation`。
