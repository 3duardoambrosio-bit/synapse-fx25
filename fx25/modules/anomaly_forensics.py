class MetricSanityChecker:
    """Detecta métricas que son demasiado buenas para ser verdad"""
    
    def verify_metric_realism(self, metrics: dict) -> dict:
        """¿Es esta métrica REALMENTE posible?"""
        
        issues = []
        
        # ROAS > 20x es CASI SIEMPRE sospechoso
        if metrics.get("roas", 0) > 20:
            issues.append({
                "severity": "CRITICAL",
                "finding": "ROAS > 20x detectado",
                "possible_causes": [
                    "Tracking error (eventos duplicados)",
                    "Atribución incorrecta",
                    "Niche market temporal (va a desaparecer)",
                    "Fraude de datos"
                ],
                "recommendation": "Verificar tracking con UTM manual"
            })
        
        # Profit > 90% es CASI SIEMPRE insostenible
        if metrics.get("profit_margin", 0) > 0.85:
            issues.append({
                "severity": "WARNING",
                "finding": "Margen > 85% es insostenible a largo plazo",
                "possible_causes": [
                    "Falta costos indirectos",
                    "Mercado sin competencia (temporal)",
                    "Producto de moda (ciclo de vida corto)"
                ],
                "recommendation": "Bajar expectativas, preparar defensas"
            })
        
        # Crecimiento exponencial NUNCA es linear
        if self._growth_too_linear():
            issues.append({
                "severity": "CRITICAL",
                "finding": "Crecimiento DEMASIADO perfecto",
                "possible_causes": [
                    "Simulación en lugar de datos reales",
                    "Datos manipulados",
                    "Falta de complejidad (fake)"
                ],
                "recommendation": "Verificar fuente de datos"
            })
        
        return {
            "metrics_realistic": len(issues) == 0,
            "sanity_issues": issues,
            "confidence_score": self._calculate_confidence(issues)
        }
class MultiAgentDebateEngine:
    """Múltiples "cerebros" debaten antes de decisión"""
    
    def __init__(self):
        self.agents = {
            "conservative": "¿Y si todo falla?",
            "growth": "¿Cómo maximizo oportunidad?",
            "data": "¿Qué dicen los números?",
            "market": "¿Qué hace la competencia?"
        }
    
    async def consensus_decision(self, scenario: dict) -> dict:
        """Debate estructurado antes de decidir"""
        
        # Cada agente da opinión independiente
        opinions = {}
        for agent_name, agent_question in self.agents.items():
            opinion = await self._get_agent_opinion(agent_name, scenario)
            opinions[agent_name] = opinion
        
        # Identifica DESACUERDOS (eso es importante)
        disagreements = self._find_disagreements(opinions)
        
        if disagreements:
            # Si hay desacuerdos, no decides rápido
            return {
                "decision": "HOLD - Multiple perspectives in conflict",
                "agents_agree": False,
                "disagreements": disagreements,
                "recommendation": "Recolectar más datos antes de decidir"
            }
        
        # Si todos acuerdan, puedes confiar
        return {
            "decision": "GO - All agents aligned",
            "confidence": 0.95,
            "reasoning": opinions
        }
class BlackSwanSurvivalKit:
    """Plan para lo impredecible"""
    
    def __init__(self):
        self.survival_scenarios = {
            "shopify_outage_48h": {
                "trigger": "Shopify API down",
                "backup_plan": "Cargar inventario a Amazon, WooCommerce",
                "revenue_impact": "-100% for 48h",
                "recovery_time": "2-4 horas"
            },
            "payment_processor_banned": {
                "trigger": "Stripe/PayPal bans account",
                "backup_plan": "Usar Wise, 2Checkout, Payoneer",
                "revenue_impact": "-80% temporarily",
                "recovery_time": "24-48 horas"
            },
            "supplier_collapse": {
                "trigger": "Main supplier goes bankrupt",
                "backup_plan": "Have list of 3 alt suppliers pre-vetted",
                "revenue_impact": "-30-50% for days",
                "recovery_time": "1-2 semanas"
            }
        }
    
    def calculate_survival_runway(self) -> dict:
        """¿Cuántos meses sobrevives sin revenue?"""
        
        monthly_burn = self._get_fixed_costs()
        cash_reserve = self._get_cash_on_hand()
        survival_months = cash_reserve / monthly_burn if monthly_burn > 0 else float('inf')
        
        return {
            "survival_months": survival_months,
            "runway_status": self._get_runway_color(survival_months),
            "recommendation": self._get_action_based_on_runway(survival_months)
        }
    
    async def activate_survival_mode(self, scenario: str):
        """Cuando ocurre lo impensable"""
        plan = self.survival_scenarios.get(scenario)
        if plan:
            await self._execute_backup_plan(plan)
            await self._notify_team(f"SURVIVAL MODE: {scenario}")
