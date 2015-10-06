from django.db import models

# Create your models here.

class Current_RouteQos_Here(models.Model):
    RouteName = models.CharField(max_length=64, primary_key=True)
    BaseTime = models.IntegerField()
    TrafficTime = models.IntegerField()
    JamFactor = models.FloatField()
    Distance = models.IntegerField()
    CollectTime = models.DateTimeField(null=True)

    def __unicode__(self):
	return self.RouteName


class Current_RouteQos_Tsi(models.Model):
    RouteId = models.CharField(max_length=8, primary_key=True)
    RouteName = models.CharField(max_length=64)
    Level = models.IntegerField()
    Speed = models.IntegerField()
    Distance = models.IntegerField(null=True)
    TravelTime = models.IntegerField(null=True)
    CollectTime = models.DateTimeField(null=True)

    def __unicode__(self):
	return u'%s %s' % (self.RouteID, self.RouteName)
