import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import random


class OperationalData:
    """运营数据结构 - 供应链、生产、质量、人力"""

    def __init__(self, data: Dict[str, Any] = None):
        if data is None:
            data = {}

        # 供应链数据
        self.supply_chain = {
            "inventory_turnover": data.get('inventory_turnover', 12.5),
            "supplier_count": data.get('supplier_count', 45),
            "supplier_on_time_rate": data.get('supplier_on_time_rate', 92.0),
            "purchase_cost": data.get('purchase_cost', 500000),
            "logistics_cost": data.get('logistics_cost', 80000)
        }

        # 生产数据
        self.production = {
            "production_efficiency": data.get('production_efficiency', 87.0),
            "capacity_utilization": data.get('capacity_utilization', 78.0),
            "defect_rate": data.get('defect_rate', 2.5),
            "equipment_oee": data.get('equipment_oee', 85.0)
        }

        # 订单与交付
        self.order = {
            "order_fulfillment_rate": data.get('order_fulfillment_rate', 95.0),
            "order_lead_time": data.get('order_lead_time', 7),  # 交付周期(天)
            "return_rate": data.get('return_rate', 3.2)
        }

        # 人力资源效能
        self.hr_efficiency = {
            "employee_count": data.get('employee_count', 280),
            "productivity_per_employee": data.get('productivity_per_employee', 5300),
            "overtime_hours": data.get('overtime_hours', 450),
            "turnover_rate": data.get('turnover_rate', 8.5)
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "supply_chain": self.supply_chain,
            "production": self.production,
            "order": self.order,
            "hr_efficiency": self.hr_efficiency
        }


class COOAgent:
    """COO运营智能体 - 供应链、生产、质量、交付专家"""

    def __init__(self, name: str = "COO运营智能体"):
        self.name = name
        self.role = "企业运营优化与供应链专家"
        self.analysis_history = []

    def analyze_operations(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        全面运营分析
        相当于COO每月的运营复盘会议
        """
        print(f"\n{'=' * 60}")
        print(f"⚙️ {self.name} 开始运营分析...")
        print(f"{'=' * 60}")

        # 解析运营数据
        op_data = OperationalData(context.get('operational', {}))

        # 1. 供应链健康度分析
        supply_health = self._analyze_supply_chain(op_data.supply_chain)

        # 2. 生产效率分析
        production_efficiency = self._analyze_production(op_data.production)

        # 3. 交付能力评估
        delivery_capability = self._analyze_delivery(op_data.order)

        # 4. 人力效能分析
        hr_efficiency = self._analyze_hr_efficiency(op_data.hr_efficiency)

        # 5. 综合运营健康评分
        overall_score = self._calculate_operational_score(
            supply_health, production_efficiency,
            delivery_capability, hr_efficiency
        )

        # 6. 运营成本分析
        cost_optimization = self._analyze_operational_costs(op_data.to_dict())

        # 7. 风险识别
        risks = self._identify_operational_risks(op_data.to_dict())

        # 生成综合报告
        report = {
            "分析时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "综合运营评分": overall_score,
            "供应链健康度": supply_health,
            "生产效率": production_efficiency,
            "交付能力": delivery_capability,
            "人力效能": hr_efficiency,
            "成本优化": cost_optimization,
            "运营风险": risks,
            "核心建议": self._generate_operational_recommendations(
                overall_score, risks, op_data.to_dict()
            )
        }

        self.analysis_history.append(report)
        self._print_operational_summary(report)

        return report

    def _analyze_supply_chain(self, supply_data: Dict) -> Dict[str, Any]:
        """供应链健康度分析"""
        print("\n📦 供应链分析...")

        turnover = supply_data['inventory_turnover']
        on_time_rate = supply_data['supplier_on_time_rate']
        supplier_count = supply_data['supplier_count']

        # 供应商多元化评估
        supplier_diversity_score = min(100, supplier_count * 2)

        # 供应链稳定性评分
        stability_score = (turnover / 15 * 50) + (on_time_rate / 100 * 50)

        health_score = (stability_score + supplier_diversity_score) / 2

        # 识别供应链风险
        risks = []
        if turnover < 8:
            risks.append("库存周转慢，存在积压风险")
        if on_time_rate < 90:
            risks.append("供应商交付不稳定，影响生产计划")
        if supplier_count < 20:
            risks.append("供应商过于集中，议价能力弱且风险高")

        analysis = {
            "健康度评分": round(health_score, 1),
            "等级": "优秀" if health_score >= 80 else "良好" if health_score >= 60 else "需改善",
            "库存周转率": turnover,
            "供应商准时交付率": on_time_rate,
            "供应商数量": supplier_count,
            "主要风险": risks if risks else ["供应链相对稳定"]
        }

        print(f"   ✅ 健康度评分: {analysis['健康度评分']}分 ({analysis['等级']})")
        if risks:
            for risk in risks:
                print(f"   ⚠️ 风险: {risk}")

        return analysis

    def _analyze_production(self, production_data: Dict) -> Dict[str, Any]:
        """生产效率分析"""
        print("\n🏭 生产效率分析...")

        efficiency = production_data['production_efficiency']
        capacity_util = production_data['capacity_utilization']
        defect_rate = production_data['defect_rate']
        oee = production_data['equipment_oee']

        # 生产效率评分
        efficiency_score = (
                efficiency * 0.3 +
                capacity_util * 0.3 +
                oee * 0.4
        )

        # 质量评分（缺陷率越低越好）
        quality_score = max(0, 100 - defect_rate * 10)

        overall_score = (efficiency_score + quality_score) / 2

        # 改进建议
        suggestions = []
        if efficiency < 85:
            suggestions.append("生产效率偏低，建议优化工艺流程或培训员工")
        if capacity_util < 75:
            suggestions.append("产能利用率不足，考虑增加订单或调整班次")
        if defect_rate > 3:
            suggestions.append("不良品率偏高，需要质量管控改进")
        if oee < 80:
            suggestions.append("设备综合效率偏低，加强设备维护和管理")

        analysis = {
            "效率评分": round(overall_score, 1),
            "等级": "优秀" if overall_score >= 80 else "良好" if overall_score >= 60 else "待提升",
            "生产效率": efficiency,
            "产能利用率": capacity_util,
            "不良品率": defect_rate,
            "设备综合效率": oee,
            "改进建议": suggestions if suggestions else ["生产运营状况良好"]
        }

        print(f"   ✅ 效率评分: {analysis['效率评分']}分 ({analysis['等级']})")
        print(f"   📊 不良品率: {defect_rate}%")

        return analysis

    def _analyze_delivery(self, order_data: Dict) -> Dict[str, Any]:
        """交付能力评估"""
        print("\n📮 交付能力分析...")

        fulfillment_rate = order_data['order_fulfillment_rate']
        lead_time = order_data['order_lead_time']
        return_rate = order_data['return_rate']

        # 交付能力评分
        delivery_score = (fulfillment_rate * 0.6 + max(0, 100 - lead_time * 5) * 0.4)

        # 客户满意度（基于退货率）
        satisfaction_score = max(0, 100 - return_rate * 10)

        overall_score = (delivery_score + satisfaction_score) / 2

        analysis = {
            "交付评分": round(overall_score, 1),
            "等级": "优秀" if overall_score >= 85 else "良好" if overall_score >= 70 else "需改善",
            "订单满足率": fulfillment_rate,
            "交付周期": f"{lead_time}天",
            "退货率": return_rate,
            "客户满意度": round(satisfaction_score, 1)
        }

        print(f"   ✅ 交付评分: {analysis['交付评分']}分")
        print(f"   📦 订单满足率: {fulfillment_rate}%")
        print(f"   ⏱️ 交付周期: {lead_time}天")

        return analysis

    def _analyze_hr_efficiency(self, hr_data: Dict) -> Dict[str, Any]:
        """人力效能分析"""
        print("\n👥 人力效能分析...")

        employee_count = hr_data['employee_count']
        productivity = hr_data['productivity_per_employee']
        overtime = hr_data['overtime_hours']
        turnover = hr_data['turnover_rate']

        # 人均产出评分
        productivity_score = min(100, productivity / 50)

        # 加班合理性评分（加班太多说明效率问题）
        overtime_score = max(0, 100 - overtime / 10)

        # 人员稳定性评分
        stability_score = max(0, 100 - turnover * 5)

        overall_score = (productivity_score + overtime_score + stability_score) / 3

        analysis = {
            "效能评分": round(overall_score, 1),
            "等级": "优秀" if overall_score >= 80 else "良好" if overall_score >= 60 else "需改善",
            "员工数量": employee_count,
            "人均产出": productivity,
            "月度加班小时": overtime,
            "离职率": turnover,
            "评语": self._hr_comment(overall_score, overtime, turnover)
        }

        print(f"   ✅ 效能评分: {analysis['效能评分']}分")
        print(f"   💰 人均产出: {productivity}元/人")

        return analysis

    def _hr_comment(self, score, overtime, turnover):
        """人力效能评语"""
        if score >= 80:
            return "团队效率高，人员稳定"
        elif score >= 60:
            if overtime > 500:
                return "效率尚可，但加班偏多，需关注员工负荷"
            if turnover > 10:
                return "效率一般，人员流失需关注"
            return "团队效能正常"
        else:
            return "人力效能偏低，需要培训或流程优化"

    def _calculate_operational_score(self, supply, production, delivery, hr):
        """综合运营评分"""
        weights = {
            "供应链": 0.30,
            "生产效率": 0.25,
            "交付能力": 0.25,
            "人力效能": 0.20
        }

        total_score = (
                supply['健康度评分'] * weights['供应链'] +
                production['效率评分'] * weights['生产效率'] +
                delivery['交付评分'] * weights['交付能力'] +
                hr['效能评分'] * weights['人力效能']
        )

        return {
            "综合得分": round(total_score, 1),
            "等级": "优秀" if total_score >= 80 else "良好" if total_score >= 60 else "待改善",
            "各维度权重": weights
        }

    def _analyze_operational_costs(self, op_data: Dict) -> Dict[str, Any]:
        """运营成本分析与优化"""
        print("\n💰 运营成本分析...")

        supply_chain = op_data['supply_chain']
        hr = op_data['hr_efficiency']

        # 计算各项成本
        logistics_cost = supply_chain['logistics_cost']
        purchase_cost = supply_chain['purchase_cost']

        # 人力相关成本（假设人均成本）
        avg_cost_per_employee = 8000  # 人均月成本
        total_hr_cost = hr['employee_count'] * avg_cost_per_employee

        # 加班成本（按1.5倍工资计算）
        overtime_cost = hr['overtime_hours'] * (avg_cost_per_employee / 22 / 8 * 1.5)

        total_op_cost = logistics_cost + purchase_cost + total_hr_cost + overtime_cost

        # 成本优化机会
        optimizations = []

        if logistics_cost > 100000:
            optimizations.append(f"物流成本偏高({logistics_cost:,.0f}元)，建议优化配送路线或谈判运费")

        if overtime_cost > 20000:
            optimizations.append(f"加班成本{overtime_cost:,.0f}元，建议增加人手或优化排班")

        if hr['productivity_per_employee'] < 6000:
            optimizations.append("人均产出偏低，建议培训或流程优化以提升人效")

        analysis = {
            "总运营成本": round(total_op_cost, 2),
            "成本构成": {
                "物流成本": logistics_cost,
                "采购成本": purchase_cost,
                "人力成本": total_hr_cost,
                "加班成本": round(overtime_cost, 2)
            },
            "优化机会": optimizations if optimizations else ["成本结构合理，暂无优化空间"],
            "预期节省": round(overtime_cost * 0.3 + logistics_cost * 0.15, 2) if optimizations else 0
        }

        print(f"   💸 总运营成本: {total_op_cost:,.2f}元")
        if optimizations:
            print(f"   💡 预计节省: {analysis['预期节省']:,.2f}元/月")

        return analysis

    def _identify_operational_risks(self, op_data: Dict) -> List[Dict]:
        """识别运营风险"""
        print("\n⚠️ 运营风险识别...")

        risks = []

        # 供应链风险
        supply = op_data['supply_chain']
        if supply['inventory_turnover'] < 8:
            risks.append({
                "风险类型": "供应风险",
                "等级": "中",
                "描述": f"库存周转率{supply['inventory_turnover']}，存在积压或断货风险"
            })

        if supply['supplier_on_time_rate'] < 90:
            risks.append({
                "风险类型": "供应风险",
                "等级": "高",
                "描述": f"供应商准时率{supply['supplier_on_time_rate']}%，影响生产计划"
            })

        # 生产风险
        prod = op_data['production']
        if prod['defect_rate'] > 3:
            risks.append({
                "风险类型": "质量风险",
                "等级": "中",
                "描述": f"不良品率{prod['defect_rate']}%，影响客户满意度"
            })

        if prod['equipment_oee'] < 80:
            risks.append({
                "风险类型": "设备风险",
                "等级": "中",
                "描述": f"设备OEE{prod['equipment_oee']}%，产能利用率低"
            })

        # 交付风险
        order = op_data['order']
        if order['order_fulfillment_rate'] < 95:
            risks.append({
                "风险类型": "交付风险",
                "等级": "高",
                "描述": f"订单满足率{order['order_fulfillment_rate']}%，影响客户体验"
            })

        # 人力风险
        hr = op_data['hr_efficiency']
        if hr['turnover_rate'] > 10:
            risks.append({
                "风险类型": "人力风险",
                "等级": "中",
                "描述": f"员工离职率{hr['turnover_rate']}%，团队稳定性差"
            })

        if hr['overtime_hours'] > 600:
            risks.append({
                "风险类型": "人力风险",
                "等级": "中",
                "描述": f"月均加班{hr['overtime_hours']}小时，员工疲劳度高"
            })

        if not risks:
            risks.append({
                "风险类型": "整体评估",
                "等级": "低",
                "描述": "运营状况良好，风险可控"
            })

        # 打印风险
        for risk in risks:
            print(f"   {risk['等级']} - {risk['风险类型']}: {risk['描述']}")

        return risks

    def _generate_operational_recommendations(self, score: Dict,
                                              risks: List[Dict],
                                              op_data: Dict) -> List[str]:
        """生成运营优化建议"""
        print("\n💡 生成运营优化建议...")

        recommendations = []

        # 基于综合评分
        if score['综合得分'] < 60:
            recommendations.append("运营效率偏低，建议启动全面运营优化项目")
        elif score['综合得分'] < 70:
            recommendations.append("运营存在提升空间，建议重点改善薄弱环节")

        # 基于风险
        for risk in risks:
            if risk['等级'] == '高':
                if '供应' in risk['风险类型']:
                    recommendations.append("供应链风险高，建议增加备选供应商和库存缓冲")
                elif '交付' in risk['风险类型']:
                    recommendations.append("交付能力不足，建议扩充产能或优化排程")
            elif risk['等级'] == '中':
                if '质量' in risk['风险类型']:
                    recommendations.append("质量管控需加强，建议实施全面质量管理")
                elif '人力' in risk['风险类型']:
                    recommendations.append("人力效能需提升，建议培训和流程优化")

        # 数据驱动建议
        if op_data['supply_chain']['inventory_turnover'] < 8:
            recommendations.append("库存周转慢，建议实施JIT或优化采购计划")

        if op_data['production']['production_efficiency'] < 85:
            recommendations.append("生产效率偏低，建议流水线优化或自动化升级")

        if op_data['order']['order_lead_time'] > 10:
            recommendations.append("交付周期长，建议优化生产流程或增加班次")

        if not recommendations:
            recommendations.append("运营状况良好，建议保持现有策略并寻找创新机会")

        return recommendations[:5]  # 返回前5条最重要的

    def _print_operational_summary(self, report: Dict):
        """打印运营分析摘要"""
        print(f"\n{'=' * 60}")
        print(f"⚙️ 运营分析摘要")
        print(f"{'=' * 60}")
        print(f"📊 综合评分: {report['综合运营评分']['综合得分']}分")
        print(f"🏥 运营等级: {report['综合运营评分']['等级']}")

        print(f"\n📦 供应链: {report['供应链健康度']['等级']}")
        print(f"🏭 生产效率: {report['生产效率']['等级']}")
        print(f"📮 交付能力: {report['交付能力']['等级']}")
        print(f"👥 人力效能: {report['人力效能']['等级']}")

        print(f"\n💰 成本优化机会: {len(report['成本优化']['优化机会'])}项")
        print(f"   预计节省: {report['成本优化']['预期节省']:,.2f}元/月")

        print(f"\n⚠️ 运营风险: {len([r for r in report['运营风险'] if r['等级'] != '低'])}项待关注")

        print(f"\n💡 核心建议:")
        for i, rec in enumerate(report['核心建议'][:3], 1):
            print(f"   {i}. {rec}")

        print(f"\n{'=' * 60}")


def demo_coo():
    """独立演示COO智能体"""
    print("=" * 60)
    print("⚙️ COO运营智能体独立演示")
    print("=" * 60)

    coo = COOAgent()

    # 模拟从指挥中心接收的企业数据
    context = {
        'operational': {
            'inventory_turnover': 12.5,
            'supplier_count': 45,
            'supplier_on_time_rate': 92.0,
            'purchase_cost': 500000,
            'logistics_cost': 80000,
            'production_efficiency': 87.0,
            'capacity_utilization': 78.0,
            'defect_rate': 2.5,
            'equipment_oee': 85.0,
            'order_fulfillment_rate': 95.0,
            'order_lead_time': 7,
            'return_rate': 3.2,
            'employee_count': 280,
            'productivity_per_employee': 5300,
            'overtime_hours': 450,
            'turnover_rate': 8.5
        }
    }

    # 运营分析
    report = coo.analyze_operations(context)

    print(f"\n{'=' * 60}")
    print("✅ COO智能体演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    demo_coo()