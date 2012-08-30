from django import template
from django.db.models import Min, Max

from aggregator.models import Feed, Entry

register = template.Library()


class FeedListNode(template.Node):

    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        context[self.var_name] = Feed.objects.filter(is_defunct=False)
        return ''


@register.tag
def get_feed_list(parser, token):
    """{% get_feed_list as feed_list %}"""
    bits = token.split_contents()
    if len(bits) != 3:
        raise template.TemplateSyntaxError, \
                "'%s' tag takes two arguments" % bits[0]

    if bits[1] != "as":
        raise template.TemplateSyntaxError, \
                "First argument to '%s' tag must be 'as'" % bits[0]

    return FeedListNode(bits[2])


class EntryNode(template.Node):

    def __init__(self, var_name, count):
        self.var_name = var_name
        self.count = int(count)

    def render(self, context):
        context[self.var_name] = Entry.objects.select_related()[:self.count]
        return ''


@register.tag
def get_entries(parser, token):
    """{% get_entries 30 as entries %}"""
    bits = token.split_contents()
    if len(bits) != 4:
        raise template.TemplateSyntaxError, \
                "'%s' tag takes three arguments" % bits[0]

    if bits[2] != 'as':
        raise template.TemplateSyntaxError, \
                "Second argument to '%s' tag must be 'as'" % bits[0]

    return EntryNode(bits[3], bits[1])



class EntrySummaryNode(template.Node):

    def __init__(self, var_name):
        self.var_name = var_name
        
        try:
            self.year_start = Entry.objects.values('date').annotate(Min("date")).order_by('-date__min')[0]['date__min'].year
        except IndexError, e:
            self.year_start = 0

        try:
            self.year_end = Entry.objects.values('date').annotate(Max("date")).order_by('date__max')[0]['date__max'].year
        except IndexError, e:
            self.year_end = 0

    def summarize(self):
        """ create summary """
        summary = {}
        for year in range(self.year_start, self.year_end + 1):
                months = Entry.objects.filter(date__year=year).dates('date','month', 'DESC')
                months = [month.strftime('%B') for month in months ]
                summary[year] = months

        return summary

    def render(self, context):
        context[self.var_name] = self.summarize()
        return ''
        

@register.tag
def get_entry_summary(parser, token):
    """{% get_entry_summary as entries %}"""
    bits = token.split_contents()

    if len(bits) != 3:
        raise template.TemplateSyntaxError, \
                "'%s' tag takes two arguments" % bits[0]

    if bits[1] != 'as':
        raise template.TemplateSyntaxError, \
                "First argument to '%s' tag must be 'as'" % bits[0]

    return EntrySummaryNode(bits[2])





