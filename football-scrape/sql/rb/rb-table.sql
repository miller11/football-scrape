select
pfy.Year as player_year,
pfy.player as player_name,
pfy.player_Link,
pfy.age,
pfy.g as games_played,
avg(pfy.g)
  OVER (
    PARTITION BY pfy.player_Link
    ORDER BY pfy.Year
  ) AS games_played_avg,
pfy.gs as games_started,
avg(pfy.gs)
  OVER (
    PARTITION BY pfy.player_Link
    ORDER BY pfy.Year
  ) AS games_started_avg,
pfy.rush_att,
pfy.rush_yds,
pfy.rush_yds_per_att,
pfy.rush_td,
pfy.targets,
pfy.rec,
pfy.rec_yds,
pfy.rec_yds_per_rec,
pfy.rec_td,
pfy.fumbles,
COALESCE(pfy.fumbles_lost, 0) as fumbles_lost,
pfy.all_td,
((pfy.rush_yds / tmy.rushing_yds) * 100) as player_yds_pct,
((pfy.rush_att / tmy.rushing_att) * 100) as player_att_pct,
tmy.wins as team_wins,
tmy.points_per_game as tm_pts_per_game,
tmy.points_against_per_game as tm_pts_per_against,
tmy.yds as tm_total_yds,
tmy.yards_per_offensive_play,
tmy.rushing_att as tm_rush_att,
tmy.rushing_yds as tm_rush_yds,
tmy.yds_per_rushing_att as tm_yds_per_att_rush,
tmy.first_downs_by_rushing as tm_first_downs_rush,
pfpy.fantasy_rank_pos prev_year_rank,
case when tmpy.coach_link = tmy.coach_link then 1 else 0 end as same_head_coach,
case when tmpy.off_coach_link = tmy.off_coach_link then 1 else 0 end as same_off_coach,
COALESCE(pfy.fantasy_rank_pos - pfpy.fantasy_rank_pos, 0) as pos_rank_change,
avg(pfy.fantasy_rank_pos)
  OVER (
    PARTITION BY pfy.player_Link
    ORDER BY pfy.Year
  ) AS fantasy_rank_pos_avg,
STDDEV(pfy.fantasy_rank_pos)
  OVER (
    PARTITION BY pfy.player_Link
    ORDER BY pfy.Year
  ) AS fantasy_rank_pos_stddev,
COUNT(*)
  OVER (
    PARTITION BY pfy.player_Link
    ORDER BY pfy.Year
  ) AS years_active,
    SUM(IF(pfy.fantasy_rank_pos < 10, 1, 0))
  OVER (
    PARTITION BY pfy.player_Link
    ORDER BY pfy.Year
  ) AS in_top_10,
    SUM(IF(pfy.fantasy_rank_pos < 25, 1, 0))
  OVER (
    PARTITION BY pfy.player_Link
    ORDER BY pfy.Year
  ) AS in_top_25,
  STDDEV(pfy.fantasy_points)
  OVER (
    PARTITION BY pfy.player_Link
    ORDER BY pfy.Year
  ) AS fantasy_points_stdev,
pfy.fantasy_rank_pos,
pfny.fantasy_points,
pfny.fantasy_points_ppr
from footballDataset.player_fantasy_year pfy
left join footballDataset.player_fantasy_year pfny on pfy.player_link = pfny.player_Link and (pfy.Year + 1) = pfny.Year
left join footballDataset.player_fantasy_year pfpy on pfy.player_link = pfpy.player_Link and (pfy.Year - 1) = pfpy.Year
left join footballDataset.team_year tmy on tmy.team_link = pfy.team_Link
left join footballDataset.team_year tmpy on tmpy.team_link = pfpy.team_Link
where ((pfy.fantasy_pos is null and pfy.rush_att > 75) or pfy.fantasy_pos = 'RB')
and pfny.fantasy_points is not null;