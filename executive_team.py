import json
import time
import random
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd
from sqlalchemy import create_engine
import sqlite3

# ==================== 智能体导入（确保文件同目录） ====================
from cfo_agent import CFOAgent
from coo_agent import COOAgent
from cto_agent import CTOAgent


# 数据库导入（暂时注释，后续可根据需要实现）
# from db_config import get_engine

# ==================== 企业业务上下文 ====================
class BusinessContext:
    """企业统一数据上下文"""

    def __init__(self):
        # 财务
        self.financial_data = {
            "revenue": 1500000, "cost": 1200000, "profit": 300000,
            "cash_flow": 500000, "profit_margin": 20.0,
            "accounts_receivable": 200000, "accounts_payable": 150000, "inventory_value": 800000
        }
        # 运营
        self.operational_data = {
            "inventory_turnover": 12.5, "supplier_count": 45, "supplier_on_time_rate": 92.0,
            "purchase_cost": 500000, "logistics_cost": 80000, "production_efficiency": 87.0,
            "capacity_utilization": 78.0, "defect_rate": 2.5, "equipment_oee": 85.0,
            "order_fulfillment_rate": 95.0, "order_lead_time": 7, "return_rate": 3.2,
            "employee_count": 280, "productivity_per_employee": 5300,
            "overtime_hours": 450, "turnover_rate": 8.5
        }
        # 市场
        self.market_data = {
            "customer_satisfaction": 4.2, "market_share": 15.8,
            "competitor_count": 8, "growth_rate": 25.0
        }
        # 技术
        self.technical_data = {
            "system_count": 24, "microservice_count": 18, "api_count": 156, "server_count": 35,
            "debt_score": 65, "legacy_system_count": 6, "code_smell_count": 45, "bug_count": 12,
            "deployment_frequency": 12, "lead_time": 3.5, "test_coverage": 78.5, "review_efficiency": 85.0,
            "avg_response_time": 120, "system_uptime": 99.5, "error_rate": 0.5, "throughput": 1500,
            "rd_budget": 300000, "rd_team_size": 25, "rd_project_count": 8
        }
        # 风险
        self.risk_data = {
            "financial_risk": "中", "supply_risk": "低",
            "market_risk": "中", "tech_risk": "中"
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "financial": self.financial_data,
            "operational": self.operational_data,
            "market": self.market_data,
            "technical": self.technical_data,
            "risk": self.risk_data,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def update_random(self):
        """模拟业务数据随机波动"""
        self.financial_data['revenue'] *= random.uniform(0.95, 1.05)
        self.financial_data['profit_margin'] += random.uniform(-1, 1)
        self.operational_data['production_efficiency'] += random.uniform(-2, 2)
        self.operational_data['defect_rate'] += random.uniform(-0.3, 0.3)
        self.technical_data['debt_score'] += random.uniform(-2, 2)
        self.technical_data['avg_response_time'] += random.uniform(-10, 10)


# ==================== CEO 智能体 ====================
class CEOAgent:
    def __init__(self, name: str = "CEO智能体"):
        self.name = name
        self.role = "企业战略决策总指挥"
        self.memory = []

    def _synthesize_decision_v2(self, financial_report, operational_report, technical_report):
        print(f"\n{'=' * 60}")
        print(f"{self.name} 综合决策中...")
        print(f"{'=' * 60}")

        finance_score = financial_report['财务健康度评分']['综合评分']
        op_score = operational_report['综合运营评分']['综合得分']
        tech_score = technical_report['综合技术评分']['综合得分']

        print(f"\n各部门评分：")
        print(f"   CFO: {finance_score}分 ({financial_report['财务健康度评分']['健康等级']})")
        print(f"   COO: {op_score}分 ({operational_report['综合运营评分']['等级']})")
        print(f"   CTO: {tech_score}分 ({technical_report['综合技术评分']['等级']})")

        if finance_score < 60:
            strategy = "紧急财务优化，控制成本，提升现金流"
            priority = "财务"
        elif op_score < 60:
            strategy = "运营流程再造，提升生产效率"
            priority = "运营"
        elif tech_score < 60:
            strategy = "技术架构升级，偿还技术债务"
            priority = "技术"
        else:
            strategy = "整体运营良好，适度扩张市场份额"
            priority = "市场"

        key_recommendations = []
        for rec in financial_report['建议措施'][:2]:
            key_recommendations.append(f"【财务】{rec}")
        for rec in operational_report['核心建议'][:2]:
            key_recommendations.append(f"【运营】{rec}")
        for rec in technical_report['技术投资建议'][:2]:
            key_recommendations.append(f"【技术】{rec}")

        decision = {
            "战略目标": strategy,
            "优先领域": priority,
            "财务健康评分": finance_score,
            "运营健康评分": op_score,
            "技术健康评分": tech_score,
            "核心建议": key_recommendations,
            "执行步骤": [
                "1. 立即启动优化专项",
                "2. 每周召开进度会议",
                "3. 建立KPI监控体系",
                "4. 月度复盘调整策略",
                "5. 季度评估整体效果"
            ],
            "关键KPI": f"{priority}健康评分提升20%",
            "预期效果": "3个月内企业整体运营效率提升15%"
        }

        print(f"\n最终战略决策：")
        print(f"核心目标: {strategy}")
        print(f"优先领域: {priority}")
        print(f"\n核心建议:")
        for i, rec in enumerate(key_recommendations[:4], 1):
            print(f"   {i}. {rec}")
        return decision

    def make_decision(self, context: BusinessContext):
        return self._synthesize_decision_v2(
            {"财务健康度评分": {"综合评分": 70, "健康等级": "良好"}, "建议措施": []},
            {"综合运营评分": {"综合得分": 75, "等级": "良好"}, "核心建议": []},
            {"综合技术评分": {"综合得分": 72, "等级": "良好"}, "技术投资建议": []}
        )

    def execute(self, decision: Dict):
        print(f"\n{'=' * 60}")
        print(f"{self.name} 执行决策...")
        print(f"{'=' * 60}")
        print(f"战略目标：{decision['战略目标']}")
        print("\n执行计划：")
        for step in decision['执行步骤']:
            print(f"   → {step}")
        print(f"\n决策执行启动完成！")
        print(f"目标: {decision['关键KPI']}")
        print(f"预期: {decision['预期效果']}")


# ==================== 高管指挥中心 ====================
class ExecutiveTeam:
    def __init__(self):
        print("正在初始化企业数字大脑系统...")
        self.ceo = CEOAgent()
        self.cfo = CFOAgent()
        self.coo = COOAgent()
        self.cto = CTOAgent()
        self.context = BusinessContext()
        self.decision_history = []
        print("高管团队智能体初始化完成！")
        print(f"   CEO: {self.ceo.name}")
        print(f"   CFO: {self.cfo.name}")
        print(f"   COO: {self.coo.name}")
        print(f"   CTO: {self.cto.name}")
        print("=" * 60)

    def execute_monthly_review(self):
        print("\n" + "=" * 60)
        print("月度经营分析会启动")
        print("=" * 60)
        print(f"\n{self.ceo.name}：各位，开始月度复盘！")

        print(f"\n{self.cfo.name}：下面是财务分析...")
        financial_report = self.cfo.analyze_financial_health(self.context.to_dict())
        time.sleep(1)

        print(f"\n{self.coo.name}：运营状况如下...")
        operational_report = self.coo.analyze_operations(self.context.to_dict())
        time.sleep(1)

        print(f"\n{self.cto.name}：技术架构评估...")
        technical_report = self.cto.analyze_technology(self.context.to_dict())
        time.sleep(1)

        print(f"\n{self.ceo.name}：基于各部门汇报，我做如下决策...")
        decision = self.ceo._synthesize_decision_v2(financial_report, operational_report, technical_report)
        self.ceo.execute(decision)

        self.decision_history.append({
            "时间": datetime.now().isoformat(),
            "财务报告": financial_report,
            "运营报告": operational_report,
            "技术报告": technical_report,
            "决策": decision
        })
        return {
            "财务报告": financial_report, "运营报告": operational_report,
            "技术报告": technical_report, "决策": decision
        }

    def crisis_simulation(self, crisis_type: str):
        print("\n" + "=" * 60)
        print(f"危机模拟启动: {crisis_type}")
        print("=" * 60)
        if crisis_type == "供应链中断":
            self.context.operational_data['supplier_on_time_rate'] = 45
            self.context.operational_data['order_fulfillment_rate'] = 60
            print("供应商停工，交付严重影响")
        elif crisis_type == "财务危机":
            self.context.financial_data['cash_flow'] = 50000
            self.context.financial_data['profit_margin'] = 5
            print("现金流严重不足")
        elif crisis_type == "技术故障":
            self.context.technical_data['system_uptime'] = 85
            self.context.technical_data['error_rate'] = 8
            print("核心系统故障")
        print(f"\n{self.ceo.name}：启动应急预案！")
        decision = self.ceo.make_decision(self.context)
        return decision

    def get_dashboard(self) -> Dict[str, Any]:
        print("\n" + "=" * 60)
        print("企业运营仪表盘")
        print("=" * 60)
        ctx = self.context.to_dict()
        dashboard = {
            "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "财务健康": {
                "利润率": f"{ctx['financial']['profit_margin']:.1f}%",
                "现金流": f"{ctx['financial']['cash_flow']:,.0f}元",
                "状态": "良好" if ctx['financial']['profit_margin'] > 15 else "预警"
            },
            "运营健康": {
                "生产效率": f"{ctx['operational']['production_efficiency']:.1f}%",
                "交付满足率": f"{ctx['operational']['order_fulfillment_rate']:.1f}%",
                "状态": "良好" if ctx['operational']['production_efficiency'] > 85 else "预警"
            },
            "技术健康": {
                "系统可用性": f"{ctx['technical']['system_uptime']:.1f}%",
                "债务评分": ctx['technical']['debt_score'],
                "状态": "良好" if ctx['technical']['system_uptime'] > 99 else "预警"
            },
            "风险提示": self._aggregate_risks()
        }
        print(
            f"\n财务: {dashboard['财务健康']['状态']} | 运营: {dashboard['运营健康']['状态']} | 技术: {dashboard['技术健康']['状态']}")
        return dashboard

    def _aggregate_risks(self) -> List[str]:
        risks = []
        if self.context.financial_data['profit_margin'] < 10:
            risks.append("财务风险：利润率偏低")
        if self.context.operational_data['defect_rate'] > 3:
            risks.append("运营风险：产品质量问题")
        if self.context.technical_data['system_uptime'] < 99:
            risks.append("技术风险：系统稳定性不足")
        return risks if risks else ["暂无重大风险"]

    def strategic_planning(self, quarters=4):
        print("\n" + "=" * 60)
        print(f"战略规划（未来{quarters}季度）")
        print("=" * 60)
        strategy = {
            "Q1": "财务优化 + 成本控制",
            "Q2": "运营流程再造 + 自动化",
            "Q3": "技术架构升级 + 中台建设",
            "Q4": "数字化转型验收"
        }
        for q, v in strategy.items():
            print(f"{q}: {v}")
        return strategy

    def run_analysis(self, context: BusinessContext):
        # 这里放你原来的分析逻辑！
        # 比如：
        # 1. 调用CFOAgent分析财务数据
        cfo_result = CFOAgent().analyze_finance(context.financial_data)
        # 2. 调用COOAgent分析运营数据
        coo_result = COOAgent().analyze_operation(context.financial_data)
        # 3. 汇总结果
        final_result = {
            "cfo_analysis": cfo_result,
            "coo_analysis": coo_result,
            "ceo_summary": "企业运营状况良好，建议优化现金流"
        }
        # 把结果存到context里
        context.health_score = 85  # 示例健康评分
        context.risk_warning = "无重大风险"  # 示例风险预警
        # 返回最终结果
        return final_result


def anaylises():
    team = ExecutiveTeam()
    result = team.execute_monthly_review()
    print("#############################################")
    # print(result['财务报告'])
    caiwu = result['财务报告']
    chengben = caiwu['成本结构分析']['成本构成']
    print(caiwu['成本结构分析'])
    jiegou_fenxi = []
    for key, value in chengben.items():
        jiegou_fenxi.append(value)
    # for key,value in caiwu.items():
    #     print(key)
    #     print("*****************")
    #     print(value)
    return jiegou_fenxi


# ==================== 主菜单 ====================
def main_menu():
    print("=" * 70)
    print("企业数字大脑系统 - 多智能体协作指挥中心")
    print("=" * 70)
    team = ExecutiveTeam()

    while True:
        print("\n" + "=" * 70)
        print("1. 月度经营分析会")
        print("2. 危机模拟处理")
        print("3. 企业运营仪表盘")
        print("4. 战略规划")
        print("5. 刷新业务数据")
        print("6. CFO独立分析")
        print("7. COO独立分析")
        print("8. CTO独立分析")
        print("0. 退出系统")
        print("=" * 70)
        choice = input("请输入选项：").strip()

        if choice == "1":
            team.execute_monthly_review()
        elif choice == "2":
            print("1.供应链中断 2.财务危机 3.技术故障")
            c = input("选择危机：")
            types = ["", "供应链中断", "财务危机", "技术故障"]
            if c in ["1", "2", "3"]:
                team.crisis_simulation(types[int(c)])
        elif choice == "3":
            team.get_dashboard()
        elif choice == "4":
            team.strategic_planning()
        elif choice == "5":
            team.context.update_random()
            print("数据已刷新")
            team.get_dashboard()
        elif choice == "6":
            team.cfo.analyze_financial_health(team.context.to_dict())
        elif choice == "7":
            team.coo.analyze_operations(team.context.to_dict())
        elif choice == "8":
            team.cto.analyze_technology(team.context.to_dict())
        elif choice == "0":
            print("\n感谢使用！")
            break
        else:
            print("无效选项")


# 读取excel表格
# def read_excel(path):
# with open(path,'r') as f:
#     f.readline()
# aa=BusinessContext()


# ==================== 启动 ====================
if __name__ == "__main__":
    # main_menu()
    anaylises()