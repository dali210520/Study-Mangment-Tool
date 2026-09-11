"""
Small helpers for validating common API query parameters.
"""
from django.utils.dateparse import parse_date
from rest_framework.exceptions import ValidationError


def get_date_param(query_params, name):
    """Return a parsed date query parameter or raise a clean API error."""
    value = query_params.get(name)
    if value in (None, ''):
        return None

    parsed_value = parse_date(value)
    if parsed_value is None:
        raise ValidationError({name: 'Use date format YYYY-MM-DD.'})
    return parsed_value


def get_int_param(query_params, name):
    """Return a positive integer query parameter or raise a clean API error."""
    value = query_params.get(name)
    if value in (None, ''):
        return None

    try:
        parsed_value = int(value)
    except (TypeError, ValueError):
        raise ValidationError({name: 'Use a numeric id.'})

    if parsed_value < 1:
        raise ValidationError({name: 'Use a numeric id.'})
    return parsed_value


def get_choice_param(query_params, name, allowed_values):
    """Return a choice query parameter if it is one of the allowed values."""
    value = query_params.get(name)
    if value in (None, ''):
        return None

    if value not in allowed_values:
        allowed = ', '.join(sorted(allowed_values))
        raise ValidationError({name: f'Use one of: {allowed}.'})
    return value


def get_ordering_param(query_params, allowed_fields):
    """Return a validated ordering parameter."""
    value = query_params.get('ordering')
    if value in (None, ''):
        return None

    field_name = value[1:] if value.startswith('-') else value
    if field_name not in allowed_fields:
        allowed = ', '.join(sorted(allowed_fields))
        raise ValidationError({'ordering': f'Use one of: {allowed}.'})
    return value


def apply_ordering(queryset, ordering, allowed_fields):
    """Apply a validated ordering parameter using an API-name-to-model-field map."""
    if not ordering:
        return queryset

    direction = '-' if ordering.startswith('-') else ''
    field_name = ordering[1:] if direction else ordering
    return queryset.order_by(f'{direction}{allowed_fields[field_name]}')

