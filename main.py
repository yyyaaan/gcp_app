import concurrent.futures
import flask
import plotly
import json
import pyarrow
import plotly.express as px
import plotly.graph_objs as go
from google.cloud import bigquery

app = flask.Flask(__name__)
bigquery_client = bigquery.Client()
QUERY = """
  select distinct route, ceiling(eur) as eur, cast(tss as DATE) as tss,
  concat(`from`, ' > ', `to`, ' on ',  FORMAT_DATE("%d%b", ddate)) as flight,
  from `yyyaaannn.Explore.QR01`
  where (`from` = '{}' and `to` = '{}' and `ddate` = DATE('{}'))
     or (`from` = '{}' and `to` = '{}' and `ddate` = DATE('{}'))
  order by flight, tss
"""


@app.route("/")
def main():

    q_route = flask.request.args.get("q_route")
    q_ddate = flask.request.args.get("q_ddate")
    q_rdate = flask.request.args.get("q_rdate")

    # override if empty
    if q_ddate is None:
        q_ddate = "2021-01-01"
    if q_rdate is None:
        q_rdate = "2021-01-06"
    if q_route is None:
        q_route = "Helsinki Sydney|Sydney Helsinki"

    q_dests = q_route.replace("|", " ").split(" ")

    query_job = bigquery_client.query(
        QUERY.format(q_dests[0], q_dests[1], q_ddate,
                     q_dests[2], q_dests[3], q_rdate))

    return flask.redirect(
        flask.url_for(
            "results",
            q_route=q_route,
            project_id=query_job.project,
            job_id=query_job.job_id,
            location=query_job.location,
        )
    )


@app.route("/results")
def results():
    project_id = flask.request.args.get("project_id")
    job_id = flask.request.args.get("job_id")
    location = flask.request.args.get("location")
    q_route = flask.request.args.get("q_route")

    query_job = bigquery_client.get_job(
        job_id, project=project_id, location=location,)

    try:
        df = query_job.result(timeout=20).to_dataframe()
    except concurrent.futures.TimeoutError:
        return flask.render_template("timeout.html", job_id=query_job.job_id)

    fig = px.bar(
        df, x='tss', y='eur', color='route', text='route',
        barmode='group', facet_row='flight',
        range_y=[0, 5000], height=900, template='plotly_white')

    fig.update_traces(hovertemplate="%{y}: %{text}")

    # add selected route
    df_sel = df[df['route'] == q_route]
    if df_sel.flight.unique().shape == (2,):
        the_df = df_sel[df_sel['flight'] == df_sel.flight.unique()[0]]
        fig.add_trace(go.Scatter(
            x=the_df.tss, y=the_df.eur, name='>>'+q_route), 2, 1)
        the_df = df_sel[df_sel['flight'] == df_sel.flight.unique()[1]]
        fig.add_trace(go.Scatter(
            x=the_df.tss, y=the_df.eur, name='>>'+q_route), 1, 1)

    # less cluster
    fig.for_each_annotation(
        lambda a: a.update(text=a.text.replace("flight=", "")))
    fig.for_each_trace(
        lambda t: t.update(name=t.name.replace("route=", "")))

    # output
    return flask.render_template(
        "result.html",
        plot=json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder),
        text="Double click to filter routes; Hover to view details")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
