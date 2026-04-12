import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import random


class FinancialData:
    """财务数据结构 - 从CEO模块接收的标准格式"""

    def __init__(self, data: Dict[str, Any] = None):
        if data is None:
            # 默认模拟数据
            self.revenue = 1500000  # 月收入
            self.cost = 1200000  # 月成本
            self.profit = 300000  # 月利润
            self.cash_flow = 500000  # 现金流
            self.profit_margin = 20.0  # 利润率
            self.accounts_receivable = 200000  # 应收账款
            self.accounts_payable = 150000  # 应付账款
            self.inventory_value = 800000  # 库存价值
        else:
            # 从CEO模块接收的数据
            self.revenue = data.get('revenue', 1500000)
            self.cost = data.get('cost', 1200000)
            self.profit = data.get('profit', 300000)
            self.cash_flow = data.get('cash_flow', 500000)
            self.profit_margin = data.get('profit_margin', 20.0)
            self.accounts_receivable = data.get('accounts_receivable', 200000)
            self.accounts_payable = data.get('accounts_payable', 150000)
            self.inventory_value = data.get('inventory_value', 800000)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "revenue": self.revenue,
            "cost": self.cost,
            "profit": self.profit,
            "cash_flow": self.cash_flow,
            "profit_margin": self.profit_margin,
            "accounts_receivable": self.accounts_receivable,
            "accounts_payable": self.accounts_payable,
            "inventory_value": self.inventory_value
        }


class CFOAgent:
    """CFO财务智能体 - 专业的财务分析与决策支持"""

    def __init__(self, name: str = "CFO财务智能体"):
        self.name = name
        self.role = "企业财务分析与决策支持专家"
        self.analysis_history = []  # 分析历史记录
        self.financial_ratios = {}  # 财务比率缓存

    def analyze_financial_health(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        全面财务健康度分析
        相当于CFO每月的财务分析报告
        """
        print(f"\n{'=' * 60}")
        print(f"💰 {self.name} 开始财务健康度分析...")
        print(f"{'=' * 60}")

        # 解析财务数据
        financial_data = context.get('financial', {})
        fd = FinancialData(financial_data)

        # 计算关键财务比率
        ratios = self._calculate_ratios(fd)

        # 财务健康评分
        health_score = self._calculate_health_score(ratios)

        # 风险识别
        risks = self._identify_risks(ratios, fd)

        # 成本结构分析
        cost_analysis = self._analyze_cost_structure(fd)

        # 现金流分析
        cash_analysis = self._analyze_cash_flow(fd)

        # 生成综合报告
        report = {
            "分析时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "财务健康度评分": health_score,
            "关键财务比率": ratios,
            "风险提示": risks,
            "成本结构分析": cost_analysis,
            "现金流分析": cash_analysis,
            "建议措施": self._generate_recommendations(ratios, risks)
        }

        # 保存到历史记录
        self.analysis_history.append(report)

        # 打印摘要
        self._print_summary(report)

        return report

    def _calculate_ratios(self, fd: FinancialData) -> Dict[str, float]:
        """计算关键财务比率"""
        print("\n📊 正在计算财务比率...")

        # 盈利能力比率
        gross_margin = ((fd.revenue - fd.cost) / fd.revenue) * 100  # 毛利率
        net_margin = fd.profit_margin  # 净利率

        # 运营效率比率
        if fd.inventory_value > 0:
            inventory_turnover = (fd.cost * 12) / fd.inventory_value  # 库存周转率（年化）
        else:
            inventory_turnover = 0

        if fd.accounts_receivable > 0:
            receivable_turnover = (fd.revenue * 12) / fd.accounts_receivable  # 应收账款周转率
        else:
            receivable_turnover = 0

        # 流动性比率
        current_ratio = fd.cash_flow / max(fd.accounts_payable, 1)  # 流动比率（简化版）

        ratios = {
            "毛利率": round(gross_margin, 2),
            "净利率": round(net_margin, 2),
            "库存周转率": round(inventory_turnover, 2),
            "应收账款周转率": round(receivable_turnover, 2),
            "流动比率": round(current_ratio, 2)
        }

        print(f"   ✓ 毛利率: {ratios['毛利率']}%")
        print(f"   ✓ 净利率: {ratios['净利率']}%")
        print(f"   ✓ 库存周转率: {ratios['库存周转率']}")
        print(f"   ✓ 应收账款周转率: {ratios['应收账款周转率']}")
        print(f"   ✓ 流动比率: {ratios['流动比率']}")

        self.financial_ratios = ratios
        return ratios

    def _calculate_health_score(self, ratios: Dict[str, float]) -> Dict[str, Any]:
        """计算综合财务健康评分"""
        print("\n🏥 正在评估财务健康度...")

        # 各项评分（0-100分）
        score_components = {}

        # 盈利能力评分（权重30%）
        profit_score = 0
        if ratios['净利率'] >= 20:
            profit_score = 100
        elif ratios['净利率'] >= 15:
            profit_score = 80
        elif ratios['净利率'] >= 10:
            profit_score = 60
        elif ratios['净利率'] >= 5:
            profit_score = 40
        else:
            profit_score = 20
        score_components['盈利能力'] = profit_score

        # 运营效率评分（权重25%）
        efficiency_score = 0
        if ratios['库存周转率'] >= 10:
            efficiency_score = 100
        elif ratios['库存周转率'] >= 8:
            efficiency_score = 80
        elif ratios['库存周转率'] >= 5:
            efficiency_score = 60
        else:
            efficiency_score = 40
        score_components['运营效率'] = efficiency_score

        # 流动性评分（权重25%）
        liquidity_score = 0
        if ratios['流动比率'] >= 3:
            liquidity_score = 100
        elif ratios['流动比率'] >= 2:
            liquidity_score = 80
        elif ratios['流动比率'] >= 1:
            liquidity_score = 60
        else:
            liquidity_score = 30
        score_components['流动性'] = liquidity_score

        # 综合评分
        weights = {'盈利能力': 0.3, '运营效率': 0.25, '流动性': 0.25}
        overall_score = sum(score * weights[k] for k, score in score_components.items())

        # 评级
        if overall_score >= 80:
            rating = "优秀"
        elif overall_score >= 60:
            rating = "良好"
        elif overall_score >= 40:
            rating = "一般"
        else:
            rating = "需改善"

        health_score = {
            "综合评分": round(overall_score, 1),
            "健康等级": rating,
            "分项评分": score_components,
            "权重配置": weights
        }

        print(f"   ✅ 综合评分: {health_score['综合评分']}分")
        print(f"   ✅ 健康等级: {health_score['健康等级']}")

        return health_score

    def _identify_risks(self, ratios: Dict[str, float],
                        fd: FinancialData) -> List[Dict[str, str]]:
        """识别财务风险"""
        print("\n⚠️ 正在识别财务风险...")

        risks = []

        # 盈利能力风险
        if ratios['净利率'] < 10:
            risks.append({
                "风险类型": "盈利风险",
                "风险等级": "高",
                "风险描述": f"净利率{ratios['净利率']}%偏低，盈利能力弱",
                "建议措施": "紧急控制成本，提高产品定价或优化产品结构"
            })
        elif ratios['净利率'] < 15:
            risks.append({
                "风险类型": "盈利风险",
                "风险等级": "中",
                "风险描述": f"净利率{ratios['净利率']}%，盈利能力待提升",
                "建议措施": "分析成本结构，寻找降本增效机会"
            })

        # 流动性风险
        if ratios['流动比率'] < 1:
            risks.append({
                "风险类型": "流动性风险",
                "风险等级": "高",
                "风险描述": f"流动比率{ratios['流动比率']}，短期偿债能力不足",
                "建议措施": "加快应收账款回收，延长应付账款周期，增加现金储备"
            })
        elif ratios['流动比率'] < 2:
            risks.append({
                "风险类型": "流动性风险",
                "风险等级": "中",
                "风险描述": f"流动比率{ratios['流动比率']}，流动性偏紧",
                "建议措施": "优化现金流管理，提高资金使用效率"
            })

        # 库存风险
        if ratios['库存周转率'] < 5:
            risks.append({
                "风险类型": "库存风险",
                "风险等级": "中",
                "风险描述": f"库存周转率{ratios['库存周转率']}，库存积压",
                "建议措施": "促销清库存，优化采购计划，实施JIT管理"
            })

        if not risks:
            risks.append({
                "风险类型": "整体评估",
                "风险等级": "低",
                "风险描述": "财务状况健康，暂无明显风险",
                "建议措施": "继续保持，可适当扩大投资"
            })

        # 打印风险摘要
        for risk in risks:
            print(f"   {risk['风险等级']} - {risk['风险类型']}: {risk['风险描述']}")

        return risks

    def _analyze_cost_structure(self, fd: FinancialData) -> Dict[str, Any]:
        """成本结构分析"""
        print("\n💸 正在分析成本结构...")

        # 成本结构（模拟更详细的成本分解）
        cost_details = {
            "原材料成本": round(fd.cost * 0.45, 2),
            "人工成本": round(fd.cost * 0.25, 2),
            "制造费用": round(fd.cost * 0.15, 2),
            "管理费用": round(fd.cost * 0.10, 2),
            "销售费用": round(fd.cost * 0.05, 2)
        }

        # 成本占比
        cost_ratios = {k: round((v / fd.cost) * 100, 2) for k, v in cost_details.items()}

        # 识别主要成本驱动因素
        cost_drivers = []
        if cost_ratios['原材料成本'] > 40:
            cost_drivers.append("原材料成本高，建议寻找替代供应商或谈判降价")
        if cost_ratios['人工成本'] > 20:
            cost_drivers.append("人工成本偏高，可考虑自动化或流程优化")
        if cost_ratios['制造费用'] > 12:
            cost_drivers.append("制造费用偏高，检查设备利用率和能源消耗")

        analysis = {
            "总成本": fd.cost,
            "成本构成": cost_details,
            "成本占比": cost_ratios,
            "优化建议": cost_drivers if cost_drivers else ["成本结构合理，保持现状"]
        }

        print(f"   💡 成本总额: {fd.cost:,.2f}元")
        for item, ratio in cost_ratios.items():
            print(f"   • {item}: {ratio}%")

        return analysis

    def _analyze_cash_flow(self, fd: FinancialData) -> Dict[str, Any]:
        """现金流分析"""
        print("\n💧 正在分析现金流...")
        # 现金流指标
        operating_cash_flow = fd.cash_flow  # 经营活动现金流
        free_cash_flow = operating_cash_flow - fd.inventory_value * 0.1  # 自由现金流（简化计算）

        # 现金转换周期（简化版）
        cash_conversion_cycle = 30  # 假设30天

        analysis = {
            "经营活动现金流": operating_cash_flow,
            "自由现金流": free_cash_flow,
            "现金转换周期(天)": cash_conversion_cycle,
            "现金流健康度": "健康" if free_cash_flow > 0 else "紧张",
            "建议": "现金流充足，可支持业务扩张" if free_cash_flow > 0 else "需要改善现金流管理"
        }

        print(f"   💰 经营现金流: {operating_cash_flow:,.2f}元")
        print(f"   🎯 自由现金流: {free_cash_flow:,.2f}元")
        print(f"   📊 健康状态: {analysis['现金流健康度']}")

        return analysis

    def _generate_recommendations(self, ratios: Dict[str, float],
                                  risks: List[Dict]) -> List[str]:
        """生成综合建议"""
        print("\n💡 正在生成财务优化建议...")

        recommendations = []

        # 基于风险的建议
        for risk in risks:
            if risk['风险等级'] in ['高', '中']:
                recommendations.append(f"【{risk['风险等级']}】{risk['建议措施']}")

        # 基于财务比率的建议
        if ratios['毛利率'] < 30:
            recommendations.append("毛利率偏低，建议重新评估定价策略或寻找低成本供应商")

        if ratios['应收账款周转率'] < 8:
            recommendations.append("应收账款周转慢，建议加强客户信用管理和催收政策")

        if ratios['库存周转率'] < 6:
            recommendations.append("库存周转较慢，建议优化库存管理，实施ABC分类管理")

        if not recommendations:
            recommendations.append("财务状况良好，建议保持现有策略并寻找增长机会")

        return recommendations

    def _print_summary(self, report: Dict[str, Any]):
        """打印分析摘要"""
        print(f"\n{'=' * 60}")
        print(f"💰 财务分析摘要")
        print(f"{'=' * 60}")
        print(f"📊 综合评分: {report['财务健康度评分']['综合评分']}分")
        print(f"🏥 健康等级: {report['财务健康度评分']['健康等级']}")
        print(f"\n⚠️ 风险提示:")

        for risk in report['风险提示']:
            print(f"   {risk['风险等级']} - {risk['风险类型']}")

        print(f"\n💡 关键建议:")
        for i, rec in enumerate(report['建议措施'][:3], 1):  # 显示前3条
            print(f"   {i}. {rec}")

        print(f"\n{'=' * 60}")

    def predict_cash_flow(self, months: int = 3) -> List[Dict[str, Any]]:
        """
        现金流预测
        预测未来几个月的现金流情况
        """
        print(f"\n{'=' * 60}")
        print(f"🔮 {self.name} 现金流预测（未来{months}个月）")
        print(f"{'=' * 60}")

        predictions = []
        base_cash_flow = 500000  # 基础现金流

        for i in range(1, months + 1):
            # 模拟季节性变化和随机波动
            seasonal_factor = 1 + 0.1 * (i % 2)  # 简单季节性
            random_factor = random.uniform(0.9, 1.1)

            predicted_flow = base_cash_flow * seasonal_factor * random_factor

            # 风险评估
            if predicted_flow < 300000:
                risk_level = "高"
                suggestion = "现金流紧张，需准备融资或削减开支"
            elif predicted_flow < 500000:
                risk_level = "中"
                suggestion = "现金流一般，谨慎管理支出"
            else:
                risk_level = "低"
                suggestion = "现金流充裕，可支持投资"

            prediction = {
                "月份": f"第{i}个月",
                "预测现金流": round(predicted_flow, 2),
                "风险等级": risk_level,
                "建议": suggestion
            }

            predictions.append(prediction)

            print(f"\n📅 {prediction['月份']}:")
            print(f"   💰 预测现金流: {prediction['预测现金流']:,.2f}元")
            print(f"   ⚠️ 风险等级: {risk_level}")
            print(f"   💡 建议: {suggestion}")

        return predictions

    def optimize_budget(self, total_budget: float,
                        departments: List[str]) -> Dict[str, float]:
        """
        预算优化分配
        根据ROI和历史数据优化预算分配
        """
        print(f"\n{'=' * 60}")
        print(f"💸 {self.name} 预算优化分配")
        print(f"{'=' * 60}")
        print(f"总预算: {total_budget:,.2f}元")
        print(f"涉及部门: {', '.join(departments)}")

        # 简化的优化算法：基于历史ROI分配
        # 实际系统中会用更复杂的模型
        historical_roi = {
            "研发部": 1.5,  # 每投入1元回报1.5元
            "市场部": 1.2,
            "销售部": 1.8,
            "生产部": 1.3,
            "管理部": 0.8
        }

        # 计算加权分配
        total_weight = sum(historical_roi.get(dept, 1.0) for dept in departments)
        budget_allocation = {}

        print("\n📊 基于ROI的预算分配方案:")
        for dept in departments:
            roi = historical_roi.get(dept, 1.0)
            weight = roi / total_weight
            allocated = total_budget * weight

            budget_allocation[dept] = round(allocated, 2)

            print(f"   {dept}: {allocated:,.2f}元 (ROI: {roi})")

        # 预期总回报
        expected_return = sum(
            budget_allocation[dept] * historical_roi.get(dept, 1.0)
            for dept in departments
        )
        print(f"\n💰 预期总回报: {expected_return:,.2f}元")
        print(f"📈 投资回报率: {(expected_return / total_budget - 1) * 100:.1f}%")

        return budget_allocation


def demo_cfo():
    """独立演示CFO智能体"""
    print("=" * 60)
    print("💰 CFO财务智能体独立演示")
    print("=" * 60)

    cfo = CFOAgent()

    # 模拟从CEO收到的企业数据
    context_from_ceo = {
        'financial': {
            'revenue': 1500000,
            'cost': 1200000,
            'profit': 300000,
            'cash_flow': 500000,
            'profit_margin': 20.0
        },
        'operational': {
            'inventory_turnover': 12.5,
            'production_efficiency': 87.0
        },
        'market': {
            'customer_satisfaction': 4.2,
            'market_share': 15.8
        }
    }

    # 1. 财务健康度分析
    report = cfo.analyze_financial_health(context_from_ceo)

    # 2. 现金流预测
    predictions = cfo.predict_cash_flow(months=3)

    # 3. 预算优化
    budget = cfo.optimize_budget(
        total_budget=1000000,
        departments=['研发部', '市场部', '销售部', '生产部']
    )

    print(f"\n{'=' * 60}")
    print("✅ CFO智能体演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    demo_cfo()