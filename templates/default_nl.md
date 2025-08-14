# Samenvatting Infrastructuurwijzigingen

## Uitvoerende Samenvatting
{% if changes.summary.total_changes > 0 %}
Deze deployment bevat **{{ changes.summary.total_changes }}** infrastructuurwijzigingen verspreid over **{{ statistics.total_stacks }}** stacks.

**Wijzigingen Overzicht:**
- ➕ **{{ changes.summary.creates }}** nieuwe resources
- 🔄 **{{ changes.summary.updates }}** bijgewerkte resources
- 🗑️ **{{ changes.summary.deletes }}** verwijderde resources
- 🔄 **{{ changes.summary.replaces }}** vervangen resources

**Risiconiveau:** {{ statistics.risk_level | format_risk_level }}

{% else %}
Geen infrastructuurwijzigingen gedetecteerd in deze deployment.
{% endif %}

## Resource Wijzigingen

{% if changes.resources %}
| Actie | Resource Type | Resource Naam | Stack |
|-------|---------------|---------------|-------|
{% for resource in changes.resources %}
{% for action in resource.actions %}
| {{ action | format_action }} | {{ resource.type | format_resource_type }} | `{{ resource.id }}` | `{{ resource.stack }}` |
{% endfor %}
{% endfor %}
{% else %}
Geen resource wijzigingen gedetecteerd.
{% endif %}

## Stack Wijzigingen

{% if changes.stacks %}
{% for stack in changes.stacks %}
### {{ stack.name }}
{% if stack.actions %}
**Stack Acties:** {% for action in stack.actions %}{{ action | format_action }}{% if not loop.last %}, {% endif %}{% endfor %}
{% endif %}

{% if stack.resources %}
**Resources:**
{% for resource in stack.resources %}
- {% for action in resource.actions %}{{ action | format_action }}{% if not loop.last %} + {% endif %}{% endfor %} {{ resource.type | format_resource_type }}: `{{ resource.id }}`
{% endfor %}
{% endif %}

{% endfor %}
{% else %}
Geen stack wijzigingen gedetecteerd.
{% endif %}

## Beveiligingsoverwegingen

{% set security_resources = changes.resources | selectattr('type', 'match', '.*IAM.*|.*KMS.*|.*SecretsManager.*|.*SecurityGroup.*') | list %}
{% if security_resources %}
**Beveiligingsgerelateerde wijzigingen gedetecteerd:**

{% for resource in security_resources %}
- **{{ resource.type | format_resource_type }}** (`{{ resource.id }}`) in stack `{{ resource.stack }}`
  {% for action in resource.actions %}- {{ action | format_action }}{% endfor %}
{% endfor %}

⚠️ **Controleer deze beveiligingsgerelateerde wijzigingen zorgvuldig voor deployment.**
{% else %}
Geen beveiligingsgerelateerde wijzigingen gedetecteerd.
{% endif %}

## Risicobeoordeling

**Risiconiveau:** {{ statistics.risk_level | format_risk_level }}

{% if statistics.risk_level == 'high' %}
🔴 **Hoge Risico Wijzigingen Gedetecteerd**
- Meerdere hoog-risico resource types worden gewijzigd
- Controleer alle wijzigingen grondig voor deployment
- Overweeg staging deployment eerst
{% elif statistics.risk_level == 'medium' %}
🟡 **Gemiddeld Risico Wijzigingen Gedetecteerd**
- Enkele risicovollere resource types betrokken
- Controleer wijzigingen voor deployment
{% else %}
🟢 **Laag Risico Wijzigingen Gedetecteerd**
- Standaard infrastructuurwijzigingen
- Ga door met normale deployment proces
{% endif %}

## Deployment Aanbevelingen

{% if statistics.total_changes > 20 %}
📋 **Grote Deployment Gedetecteerd**
- Overweeg opsplitsing in kleinere deployments
- Monitor deployment voortgang nauwlettend
- Heb rollback plan klaar
{% elif statistics.total_changes > 10 %}
📋 **Gemiddelde Deployment Gedetecteerd**
- Controleer alle wijzigingen voor deployment
- Monitor deployment voortgang
{% else %}
📋 **Kleine Deployment Gedetecteerd**
- Standaard deployment proces
- Snelle controle aanbevolen
{% endif %}

{% if security_resources %}
🔒 **Beveiligingscontrole Vereist**
- Beveiligingsgerelateerde resources worden gewijzigd
- Zorg voor juiste toegangscontroles
- Controleer IAM policies en permissies
{% endif %}

## Resource Type Verdeling

{% if statistics.resource_types %}
| Resource Type | Aantal |
|---------------|--------|
{% for resource_type, count in statistics.resource_types.items() %}
| {{ resource_type | format_resource_type }} | {{ count }} |
{% endfor %}
{% endif %}

---

**Gegenereerd door:** {{ metadata.generator }} v{{ metadata.version }}  
**Model:** {{ metadata.model }}  
**Gegenereerd:** {{ metadata.timestamp }}  
**Repository:** {{ metadata.repository }} 