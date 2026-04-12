"""
企业数字大脑系统 - CEO智能体模块
author: 小龙侠
date: 2026-03-25
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import random


class BusinessContext:
    """业务上下文 - 存储企业当前状态数据"""

    def __init__(self):
        # 模拟企业实时数据
        self.financial_data = {
            "revenue": 1500000,  # 月收入(元)
            "cost": 1200000,     # 月成本(元)
            "profit": 300000,    # 月利润(元)
            "cash_flow": 500000, # 现金流
            "profit_margin": 20.0  # 利润率(%)
        }

        self.operational_data = {
            "inventory_turnover": 12.5,  # 库存周转率
            "order_fulfillment_rate": 95.0,  # 订单满足率(%)
            "production_efficiency": 87.0,   # 生产效率(%)
            "supplier_count": 45,  # 供应商数量
            "employee_count": 280   # 员工数量
        }

        self.market_data = {
            "customer_satisfaction": 4.2,  # 客户满意度(1-5)
            "market_share": 15.8,          # 市场份额(%)
            "competitor_count": 8,         # 主要竞争对手
            "growth_rate": 25.0            # 同比增长率(%)
        }

        self.risk_data = {
            "financial_risk": "中",        # 财务风险等级
            "supply_risk": "低",           # 供应链风险
            "market_risk": "中",           # 市场风险
            "credit_risk": "低"            # 信用风险
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "financial": self.financial_data,
            "operational": self.operational_data,
            "market": self.market_data,
            "risk": self.risk_data,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def get_summary(self) -> str:
        """获取企业状态摘要"""
        return f"""
        企业现状摘要：
        财务：月收入{self.financial_data['revenue']/10000:.1f}万，利润率{self.financial_data['profit_margin']}%
        ⚙️ 运营：库存周转率{self.operational_data['inventory_turnover']}，生产效率{self.operational_data['production_efficiency']}%
        市场：市场份额{self.market_data['market_share']}%，客户满意度{self.market_data['customer_satisfaction']}/5
        ⚠️ 风险：财务风险{self.risk_data['financial_risk']}，供应链风险{self.risk_data['supply_risk']}
        """


class SimulatedAgent:
    """模拟的其他智能体(实际系统中会独立部署)"""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def analyze(self, context: BusinessContext) -> Dict[str, Any]:
        """模拟分析"""
        time.sleep(0.5)  # 模拟处理时间

        if "财务" in self.role:
            return self._financial_analysis(context)
        elif "运营" in self.role:
            return self._operational_analysis(context)
        elif "技术" in self.role:
            return self._technical_analysis(context)
        else:
            return {"status": "unknown", "message": "未知角色"}

    def _financial_analysis(self, context: BusinessContext) -> Dict:
        """财务分析"""
        profit_margin = context.financial_data['profit_margin']

        if profit_margin < 15:
            suggestion = "利润率偏低，建议削减成本或提高产品价格"
            priority = "高"
        elif profit_margin < 25:
            suggestion = "利润率健康，可考虑扩大市场投入"
            priority = "中"
        else:
            suggestion = "利润率优秀，建议加大研发投入"
            priority = "低"

        return {
            "智能体": "CFO财务智能体",
            "分析结果": f"当前利润率{profit_margin}%",
            "风险提示": f"财务风险等级：{context.risk_data['financial_risk']}",
            "建议": suggestion,
            "优先级": priority
        }

    def _operational_analysis(self, context: BusinessContext) -> Dict:
        """运营分析"""
        efficiency = context.operational_data['production_efficiency']
        turnover = context.operational_data['inventory_turnover']

        return {
            "智能体": "COO运营智能体",
            "分析结果": f"生产效率{efficiency}%，库存周转率{turnover}",
            "风险提示": f"供应链风险：{context.risk_data['supply_risk']}",
            "建议": "建议优化供应链，提升库存周转效率",
            "优先级": "中"
        }

    def _technical_analysis(self, context: BusinessContext) -> Dict:
        """技术分析"""
        return {
            "智能体": "CTO技术智能体",
            "分析结果": "系统运行正常，无技术风险",
            "风险提示": "技术债务可控",
            "建议": "建议引入AI质检系统提升生产效率",
            "优先级": "低"
        }


class CEOAgent:
    """CEO智能体 - 企业数字大脑总指挥"""

    def __init__(self):
        self.name = "CEO智能体"
        self.role = "企业战略决策总指挥"
        self.memory = []  # 短期记忆
        self.specialist_agents = {
            "财务": SimulatedAgent("张三", "财务分析师"),
            "运营": SimulatedAgent("李四", "运营优化师"),
            "技术": SimulatedAgent("王五", "技术架构师")
        }

    def perceive(self, context: BusinessContext) -> Dict[str, Any]:
        """
        感知能力：收集并理解企业当前状态
        相当于CEO每天看报表、了解各部门情况
        """
        print(f"\n{'='*60}")
        print(f"🧠 {self.name} 开始感知环境...")
        print(f"{'='*60}")

        # 获取企业现状
        current_state = context.to_dict()
        key_metrics = {
            "利润率": current_state['financial']['profit_margin'],
            "现金流": current_state['financial']['cash_flow'],
            "市场份额": current_state['market']['market_share'],
            "客户满意度": current_state['market']['customer_satisfaction'],
            "生产效率": current_state['operational']['production_efficiency']
        }

        print("📊 关键指标采集完成：")
        for k, v in key_metrics.items():
            print(f"   • {k}: {v}")

        # 存储到记忆
        self.memory.append({
            "type": "perception",
            "timestamp": datetime.now().isoformat(),
            "data": key_metrics
        })

        return key_metrics

    def reason(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        推理能力：分析当前情况，识别问题和机会
        相当于CEO开战略会议，思考公司下一步怎么走
        """
        print(f"\n{'=' * 60}")
        print(f"🤔 {self.name} 开始推理分析...")
        print(f"{'=' * 60}")

        problems = []

        # 规则引擎：根据指标识别问题
        if data['利润率'] < 20:
            problems.append({
                "领域": "财务",
                "问题": "利润率下降",
                "严重程度": "高",
                "原因": "可能是成本上升或价格竞争激烈"
            })

        if data['客户满意度'] < 4.0:
            problems.append({
                "领域": "市场",
                "问题": "客户满意度低",
                "严重程度": "中",
                "原因": "产品质量或服务质量需要提升"
            })

        if data['生产效率'] < 85:
            problems.append({
                "领域": "运营",
                "问题": "生产效率偏低",
                "严重程度": "中",
                "原因": "可能是设备老化或流程不合理"
            })

        if data['市场份额'] < 10:
            problems.append({
                "领域": "战略",
                "问题": "市场份额不足",
                "严重程度": "高",
                "原因": "竞争力不足，需要差异化策略"
            })

        if not problems:
            print("✅ 恭喜！企业当前运营状况良好，未发现明显问题")
            problems.append({
                "领域": "整体",
                "问题": "运营正常",
                "严重程度": "低",
                "原因": "各项指标健康"
            })
        else:
            print(f"⚠️ 识别出 {len(problems)} 个关键问题：")
            for i, p in enumerate(problems, 1):
                print(f"   {i}. 【{p['严重程度']}】{p['领域']}板块：{p['问题']}")
                print(f"      原因分析：{p['原因']}")

        return problems

    def make_decision(self, context: BusinessContext) -> Dict[str, Any]:
        """
        决策能力：制定战略决策并协调各智能体
        这是CEO最核心的能力：拍板+调度资源
        """
        print(f"\n{'=' * 60}")
        print(f"🎯 {self.name} 开始制定决策...")
        print(f"{'=' * 60}")

        # 第一步：感知环境
        perception_data = self.perceive(context)

        # 第二步：识别问题
        problems = self.reason(perception_data)

        # 第三步：协调专家智能体进行分析
        print(f"\n📢 {self.name}：'各部门准备汇报！'")

        expert_reports = {}
        for domain, agent in self.specialist_agents.items():
            print(f"\n   → 正在请求{agent.role}汇报...")
            report = agent.analyze(context)
            expert_reports[domain] = report
            print(f"   ← 收到{report['智能体']}报告")

        # 第四步：综合决策
        decision = self._synthesize_decision(problems, expert_reports)

        # 第五步：记录记忆
        self.memory.append({
            "type": "decision",
            "timestamp": datetime.now().isoformat(),
            "problems": problems,
            "expert_reports": expert_reports,
            "final_decision": decision
        })

        return decision

    def _synthesize_decision(self, problems: List[Dict],
                             expert_reports: Dict[str, Any]) -> Dict[str, Any]:
        """综合各方意见，做出最终决策"""
        print(f"\n{'=' * 60}")
        print(f"🎯 {self.name} 综合决策中...")
        print(f"{'=' * 60}")

        # 提取高优先级问题
        high_priority_problems = [p for p in problems if p['严重程度'] == '高']

        # 收集各专家的建议
        suggestions = []
        priorities = []

        for domain, report in expert_reports.items():
            suggestions.append(f"【{domain}】{report['建议']}")
            if report['优先级'] == '高':
                priorities.append(domain)

        # 制定战略决策（简化版决策树）
        if high_priority_problems:
            main_problem = high_priority_problems[0]
            strategy = f"优先解决{main_problem['领域']}板块的{main_problem['问题']}"
        else:
            strategy = "维持现状，加强优势领域投入"

        # 生成执行计划
        action_plan = {
            "战略目标": strategy,
            "执行步骤": [
                "1. 召开专项会议，明确责任部门",
                "2. 制定详细改进方案和时间表",
                "3. 分配资源，启动项目执行",
                "4. 每周跟踪进度，及时调整",
                "5. 月度评估效果，持续优化"
            ],
            "资源需求": "根据具体问题确定预算和人力",
            "预期效果": "3个月内关键指标改善15%以上",
            "风险提示": "执行不力可能导致效果不佳"
        }

        # 输出决策报告
        print(f"\n📄 战略决策报告：")
        print(f"   🎯 决策目标：{strategy}")
        print(f"   👥 责任部门：{', '.join(priorities) if priorities else '全员'}")
        print(f"   📊 预期效果：{action_plan['预期效果']}")

        return action_plan

    def execute(self, decision: Dict[str, Any]) -> bool:
        """
        执行能力：监督决策执行（简化版）
        实际系统中会对接ERP/CRM等系统
        """
        print(f"\n{'=' * 60}")
        print(f"⚡ {self.name} 开始执行决策...")
        print(f"{'=' * 60}")

        print(f"决策内容：{decision['战略目标']}")
        print("\n执行计划：")
        for step in decision['执行步骤']:
            print(f"   → {step}")

        # 模拟执行结果
        success_rate = random.uniform(0.7, 0.95)
        success = success_rate > 0.8

        if success:
            print(f"\n✅ 决策执行成功！预估达成率：{success_rate:.1%}")
        else:
            print(f"\n❌ 决策执行遇到阻力，需要人工干预")

        return success

def interactive_mode():
    """交互模式：让老大直接体验CEO智能体"""
    print("=" * 60)
    print("🧠 企业数字大脑系统 - CEO智能体演示")
    print("=" * 60)
    print("正在初始化，请稍候...")

    # 创建CEO智能体
    ceo = CEOAgent()
    context = BusinessContext()

    print("\n✅ CEO智能体初始化完成！")
    print("\n" + "-" * 60)
    print("📊 当前企业状态：")
    print(context.get_summary())

    while True:
        print("\n" + "=" * 60)
        print("请选择一个操作：")
        print("1. 🎯 让CEO智能体做一次完整决策")
        print("2. 📊 查看详细企业数据")
        print("3. 🔄 刷新企业数据（模拟新数据）")
        print("4. 🧠 查看CEO智能体记忆")
        print("0. ❌ 退出程序")
        print("=" * 60)

        choice = input("\n请输入选项编号（0-4）：").strip()

        if choice == "1":
            print("\n🚀 启动CEO智能体决策流程...")
            decision = ceo.make_decision(context)

            print("\n" + "-" * 60)
            print("📄 最终决策报告：")
            print(f"🎯 战略目标：{decision['战略目标']}")
            print("\n📄 详细执行计划：")
            for step in decision['执行步骤']:
                print(f"   {step}")
            print(f"\n💰 资源需求：{decision['资源需求']}")
            print(f"📊 预期效果：{decision['预期效果']}")
            print(f"⚠️ 风险提示：{decision['风险提示']}")

            # 模拟执行
            input("\n按回车键执行决策...")
            ceo.execute(decision)

        elif choice == "2":
            print("\n📊 详细企业数据：")
            print(json.dumps(context.to_dict(), indent=2, ensure_ascii=False))

        elif choice == "3":
            print("\n🔄 正在刷新企业数据...")
            # 模拟数据变化
            context.financial_data['revenue'] *= random.uniform(0.95, 1.05)
            context.financial_data['profit_margin'] += random.uniform(-2, 2)
            print("✅ 数据刷新完成！")
            print(context.get_summary())

        elif choice == "4":
            print("\n🧠 CEO智能体记忆记录：")
            if not ceo.memory:
                print("暂无记忆记录")
            else:
                for i, mem in enumerate(ceo.memory[-5:], 1):  # 显示最近5条
                    print(f"\n记录 {i}:")
                    print(f"时间：{mem['timestamp']}")
                    print(f"类型：{mem['type']}")
                    if mem['type'] == 'perception':
                        print(f"数据：{mem['data']}")
                    elif mem['type'] == 'decision':
                        print(f"战略目标：{mem['final_decision']['战略目标']}")

        elif choice == "0":
            print("\n👋 感谢使用企业数字大脑系统！")
            break

        else:
            print("❌ 无效的选项，请重新输入！")

def auto_demo():
    """自动演示模式：直接展示完整流程"""
    print("=" * 60)
    print("🎬 自动演示模式")
    print("=" * 60)

    ceo = CEOAgent()
    context = BusinessContext()

    print("\n📊 初始企业状态：")
    print(context.get_summary())

    # 运行决策
    decision = ceo.make_decision(context)
    ceo.execute(decision)

    print("\n" + "=" * 60)
    print("✅ 演示完成！")

if __name__ == "__main__":
    """
        主入口：支持两种模式
        1. 交互模式：python ceo_agent.py
        2. 自动演示：python ceo_agent.py --demo
        """
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        auto_demo()
    else:
        interactive_mode()