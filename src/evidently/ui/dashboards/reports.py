import datetime
from typing import TYPE_CHECKING
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from plotly import graph_objs as go

from evidently.base_metric import Metric
from evidently.renderers.html_widgets import CounterData
from evidently.renderers.html_widgets import counter
from evidently.renderers.html_widgets import plotly_figure
from evidently.ui.type_aliases import ProjectID

from .base import DashboardPanel
from .base import PanelValue
from .base import assign_panel_id
from .utils import CounterAgg
from .utils import PlotType
from .utils import _get_metric_hover

if TYPE_CHECKING:
    from evidently.ui.base import DataStorage


class DashboardPanelPlot(DashboardPanel):
    values: List[PanelValue]
    plot_type: PlotType

    @assign_panel_id
    def build(
        self,
        data_storage: "DataStorage",
        project_id: ProjectID,
        timestamp_start: Optional[datetime.datetime],
        timestamp_end: Optional[datetime.datetime],
    ):
        points = data_storage.load_points(project_id, self.filter, self.values, timestamp_start, timestamp_end)
        fig = go.Figure(layout={"showlegend": True})
        for val, metric_pts in zip(self.values, points):
            if len(metric_pts) == 0:
                # no matching metrics, show error?
                continue

            for metric, pts in metric_pts.items():
                pts.sort(key=lambda x: x[0])

                hover = _get_metric_hover(metric, val)
                if self.plot_type == PlotType.HISTOGRAM:
                    plot = go.Histogram(
                        x=[p[1] for p in pts],
                        name=val.legend,
                        legendgroup=val.legend,
                        hovertemplate=hover,
                    )
                else:
                    cls, args = self.plot_type_cls
                    plot = cls(
                        x=[p[0] for p in pts],
                        y=[p[1] for p in pts],
                        name=val.legend,
                        legendgroup=val.legend,
                        hovertemplate=hover,
                        **args,
                    )
                fig.add_trace(plot)
        return plotly_figure(title=self.title, figure=fig, size=self.size)

    @property
    def plot_type_cls(self):
        if self.plot_type == PlotType.SCATTER:
            return go.Scatter, {"mode": "markers"}
        if self.plot_type == PlotType.BAR:
            return go.Bar, {}
        if self.plot_type == PlotType.LINE:
            return go.Scatter, {}
        raise ValueError(f"Unsupported plot type {self.plot_type}")


class DashboardPanelCounter(DashboardPanel):
    agg: CounterAgg
    value: Optional[PanelValue] = None
    text: Optional[str] = None

    @assign_panel_id
    def build(
        self,
        data_storage: "DataStorage",
        project_id: ProjectID,
        timestamp_start: Optional[datetime.datetime],
        timestamp_end: Optional[datetime.datetime],
    ):
        if self.agg == CounterAgg.NONE:
            return counter(counters=[CounterData(self.title, self.text or "")], size=self.size)
        if self.value is None:
            raise ValueError("Counters with agg should have value")
        points = data_storage.load_points(project_id, self.filter, [self.value], timestamp_start, timestamp_end)[0]
        value = self._get_counter_value(points)
        if int(value) != value:
            ct = CounterData.float(self.text or "", value, 3)
        else:
            ct = CounterData.int(self.text or "", int(value))
        return counter(title=self.title, counters=[ct], size=self.size)

    def _get_counter_value(self, points: Dict[Metric, List[Tuple[datetime.datetime, Any]]]) -> float:
        if self.value is None:
            raise ValueError("Counters with agg should have value")
        if self.agg == CounterAgg.LAST:
            if len(points) == 0:
                return 0
            return max(
                ((ts, v) for vs in points.values() for ts, v in vs),
                key=lambda x: x[0],
            )[1]
        if self.agg == CounterAgg.SUM:
            return sum(v or 0 for vs in points.values() for ts, v in vs)
        raise ValueError(f"Unknown agg type {self.agg}")
