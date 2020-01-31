from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.db.models import Q
import pandas as pd

from plotly.offline import plot
import plotly.graph_objs as go

from .models import Players, TeamInfo
from .forms import TestForm, Customized_Tables

def index(request):
    #it works! it runs two querys and if a search term matches a first or a last name then it will return it.
    #the only way to run or on querys is to use the Q imported above and | inbetween querys
    search_term = ""

    if 'search' in request.GET:
        search_term = request.GET['search']
        players = Players.objects.filter(Q(player_lname__icontains=search_term) | Q(player_fname__icontains=search_term))
        context = {'players': players, 'search_term': search_term,}
    else:
        #I am going to use this to get our fantasy points for each player, eventually I will make the ability to customize
        default_scoring = {'solo':1,'ast':0.5,'sacks':3,'interceptions':3,'ffb':3}
        #this is pulling all of the team info database
        raw_stats = TeamInfo.objects.all()
        #this gets it so pandas can use it
        stats = raw_stats.values()
        #here we have our pandas dataframe
        df = pd.DataFrame.from_records(stats)
        #this puts in our default scoring as a column in the dataframe right now it is just based on solo tackles
        df["fp"] = df['solo']*default_scoring['solo']+df['assists']*default_scoring['ast']+df['sacks']*default_scoring['sacks']+df['interceptions']*default_scoring['interceptions']+df['ffb']*default_scoring['ffb']
        #this sorts by fantasy point totals
        df = df.sort_values(['year','fp'], ascending=[False, False])
        #sort out the top 10
        df = df[0:10]
        #list for the top ten scorers ids
        ids = df['player_id_id'].values.tolist()
        #gets the name information for the players
        players = Players.objects.filter(pk__in=ids)
        #now to get the fantasy point totals and the players id for a join
        df = df[['fp', 'player_id_id']]
        #getting the name values of the players
        final_names = players.values()
        #making a dataframe of the name info
        final_df = pd.DataFrame.from_records(final_names)
        #joins our table that is keeping track of points and the one with the players name info
        final_df = pd.merge(final_df, df, left_on='player_id', right_on='player_id_id')
        #sorts out the top 10 displayed
        final_df = final_df.sort_values(['fp'], ascending=False)
        #creating tuples to plug into the template
        tuples = [tuple(x) for x in final_df.to_numpy()]
        #the above is probably sloppy as hell but it works
        context = {'search_term': search_term, 'tuples':tuples,}

    return render(request, 'defense/index.html', context)


def player_indv(request, player_id):
    player_info = get_object_or_404(Players, pk=player_id)
    team_info = get_list_or_404(TeamInfo.objects.order_by('-year'), player_id=player_id)

    qs = TeamInfo.objects.filter(player_id=player_id)
    q = qs.values()

    #the below DataFrame we can use to generate whatever tables we want,
    df = pd.DataFrame.from_records(q).sort_values(['year'])

    #this creates a dataframe that will show in the players details screen.
    df_table = df[['year','team','age','position','g','gs','interceptions','int_td','pass_def','ffb','fr','fb_td','sacks','solo','assists','tfl','qb_hits','sfty']]
    table = df_table.sort_values(['year'], ascending=[False]).to_html()

    fig = go.Figure()
    #if this is a post request the data must be processed
    if request.method == 'POST':
        form = Customized_Tables(request.POST)

        stat_list = []
        if form.is_valid():
            cd = form.cleaned_data
            if cd.get('games'):
                stat_list.append('g')
            if cd.get('games_started'):
                stat_list.append('gs')
            if cd.get('solo_tackles'):
                stat_list.append('solo')
            if cd.get('asst_tackles'):
                stat_list.append('assists')
            if cd.get('tackle_for_loss'):
                stat_list.append('tfl')
            if cd.get('sacks'):
                stat_list.append('sacks')
            if cd.get('qb_hits'):
                stat_list.append('qb_hits')
            if cd.get('interceptions'):
                stat_list.append('interceptions')
            if cd.get('pass_def'):
                stat_list.append('pass_def')
            if cd.get('forced_fumble'):
                stat_list.append('ffb')
            if cd.get('fumble_recovery'):
                stat_list.append('fr')

        for i in stat_list:
            fig.add_trace(go.Scatter(x=df['year'],y=df[i],name=i))

            #this adds the axis settings we want
        fig.update_layout(title="Player Stats", xaxis_title="Season", width=850, height=500,
            xaxis = dict(tickmode = 'linear', dtick = 1), yaxis = dict(tickmode = 'linear', tick0 = 0, dtick = 10))

        #this set the html, css, and javascript needed for our graph to the variable plot_div, this can be passed to the template
        plot_div = plot(fig, output_type='div')

    else:
        form = Customized_Tables()
        #this is the initial instance of our graph


        #this passes in all of the stats from the pandas dataframe we want to graph, the for loop below traces them
        stat_list = ['g','gs','interceptions','int_td','pass_def','ffb','fr','fb_td','sacks','solo','assists','tfl','qb_hits']
        for i in stat_list:
            fig.add_trace(go.Scatter(x=df['year'],y=df[i],name=i))

            #this adds the axis settings we want
        fig.update_layout(title="Player Stats", xaxis_title="Season", width=850, height=500,
            xaxis = dict(tickmode = 'linear', dtick = 1), yaxis = dict(tickmode = 'linear', tick0 = 0, dtick = 10))

        #this set the html, css, and javascript needed for our graph to the variable plot_div, this can be passed to the template
        plot_div = plot(fig, output_type='div')

    context = {'player_info': player_info, 'team_info':team_info, 'table':table, 'plot_div': plot_div, 'form':form}

    return render(request, 'defense/detail.html', context)
    #this is returning the players name and stats by year if you follow the url defense/player's_id
    #it is essentially an info page for the player

def test(request):
    #it works! it runs two querys and if a search term matches a first or a last name then it will return it.
    #the only way to run or on querys is to use the Q imported above and | inbetween querys
    search_term = ""
    #I am going to use this to get our fantasy points for each player, eventually I will make the ability to customize
    default_scoring = {'solo':1,'ast':0.5,'sacks':3,'interceptions':3,'ffb':3}

        #if this is a post request the data must be processed
    if request.method == 'POST':
        #this will create instance of our form class and populate it with the data from the user input
        form = TestForm(request.POST)
        #check if it is a valid entry, if it is then it will update the default scoring dict with custom values
        if form.is_valid():
            cd = form.cleaned_data
            default_scoring['solo'] = cd.get('solo_tackles')
            default_scoring['ast'] = cd.get('ast_tackles')
            default_scoring['sacks'] = cd.get('sacks')
            default_scoring['interceptions'] = cd.get('interceptions')
            default_scoring['ffb'] = cd.get('ffb')


        #if a get or other method for will be blank
    else:
        form = TestForm()

    if 'search' in request.GET:
        search_term = request.GET['search']
        players = Players.objects.filter(Q(player_lname__icontains=search_term) | Q(player_fname__icontains=search_term))
        context = {'players': players, 'search_term': search_term,}
    else:
        #this is pulling all of the team info database
        raw_stats = TeamInfo.objects.all()
        #this gets it so pandas can use it
        stats = raw_stats.values()
        #here we have our pandas dataframe
        df = pd.DataFrame.from_records(stats)
        #this puts in our default scoring as a column in the dataframe right now it is just based on solo tackles
        df["fp"] = df['solo']*default_scoring['solo']+df['assists']*default_scoring['ast']+df['sacks']*default_scoring['sacks']+df['interceptions']*default_scoring['interceptions']+df['ffb']*default_scoring['ffb']
        #this sorts by fantasy point totals
        df = df.sort_values(['year','fp'], ascending=[False, False])
        #sort out the top 10
        df = df[0:10]
        #list for the top ten scorers ids
        ids = df['player_id_id'].values.tolist()
        #gets the name information for the players
        players = Players.objects.filter(pk__in=ids)
        #now to get the fantasy point totals and the players id for a join
        df = df[['fp', 'player_id_id']]
        #getting the name values of the players
        final_names = players.values()
        #making a dataframe of the name info
        final_df = pd.DataFrame.from_records(final_names)
        #joins our table that is keeping track of points and the one with the players name info
        final_df = pd.merge(final_df, df, left_on='player_id', right_on='player_id_id')
        #sorts out the top 10 displayed
        final_df = final_df.sort_values(['fp'], ascending=False)
        #creating tuples to plug into the template
        tuples = [tuple(x) for x in final_df.to_numpy()]
        #the above is probably sloppy as hell but it works
        context = {'search_term': search_term, 'tuples':tuples,}

    #action = ""

    #this appends the context dictionary with the form object
    context['form'] = form

    return render(request, 'defense/test.html', context)
