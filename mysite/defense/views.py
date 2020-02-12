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
    #if submit is clicked
    if 'search' in request.GET:
        #this reads what is submitted
        search_term = request.GET['search']

        try:
            #this splits the submitted info on the spaces
            search_term = search_term.split()

            if len(search_term) < 2:
                #if it is only one word submitted it will be checked against databases for last and first name
                players = Players.objects.filter(Q(player_lname__icontains=search_term[0]) | Q(player_fname__icontains=search_term[0]))

            elif len(search_term) == 2:
                #else if it is two words submitted it will be checked if both the first and last names are attached to a player
                players = Players.objects.filter((Q(player_lname__icontains=search_term[0]) & Q(player_fname__icontains=search_term[1])) | (Q(player_lname__icontains=search_term[1]) & Q(player_fname__icontains=search_term[0])))
            else:
                #if more than 2 names are given it will return the below
                players = 'No Players Found...'

        except IndexError:
            #this exception only triggers if someone submits none as a search and returns the below
            players = 'No Players Found...'
        #this updates the dictonary for the html
        header = 'Search Results'
        context = {'players': players, 'header': header,}

    else:
        #I am going to use this to get our fantasy points for each player, eventually I will make the ability to customize
        default_scoring = {'solo':1,'ast':0.5,'sacks':3,'interceptions':3,'ffb':3, 'fr':1, 'td':6, 'sfty':2,}
        #this is pulling all of the team info database
        raw_stats = TeamInfo.objects.all()
        #this gets it so pandas can use it
        stats = raw_stats.values()
        #here we have our pandas dataframe
        df = pd.DataFrame.from_records(stats)
        #this puts in our default scoring as a column in the dataframe it is calculated based on the above dictionary and a dataframe of our postgresql database
        df["fp"] = df['solo']*default_scoring['solo']+df['assists']*default_scoring['ast']+df['sacks']*default_scoring['sacks']+df['interceptions']*default_scoring['interceptions']+df['ffb']*default_scoring['ffb']+df['fr']*default_scoring['fr']+df['sfty']*default_scoring['sfty']+(df['int_td']+df['fb_td'])*default_scoring['td']
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
        #the above is probably sloppy as hell but it works try and improve efficiency later
        header = 'Top 10 Standard Scoring'
        table_headers = ['Name', 'Fantasy Points']

        context = {'tuples':tuples, 'header':header, 'table_headers':table_headers}

    return render(request, 'defense/index.html', context)

def test(request):
    #it works! it runs two querys and if a search term matches a first or a last name then it will return it.
    #the only way to run or on querys is to use the Q imported above and | inbetween querys
    #This is the default socring, the ability to update the custom scoring is below
    default_scoring = {'solo':1,'ast':0.5,'sacks':3,'interceptions':3,'ffb':3, 'fr':1, 'td':6, 'sfty':2,}

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
            default_scoring['fr'] = cd.get('fr')
            default_scoring['td'] = cd.get('td')
            default_scoring['sfty'] = cd.get('sfty')
            header = 'Top 10 Custom Scoring'

    #the else occurs only before the submit button is clicked, so essentially when the player page is first loaded
    #the graph will be populated with every data point, might decide to change it to blank for initial load later.
    else:
        form = TestForm()
        header = 'Top 10 Standard Scoring'

    #this is pulling all of the team info database
    raw_stats = TeamInfo.objects.all()
    #this gets it so pandas can use it
    stats = raw_stats.values()
    #here we have our pandas dataframe
    df = pd.DataFrame.from_records(stats)
    #this puts in our default scoring as a column in the dataframe it is calculated based on the above dictionary and a dataframe of our postgresql database
    df["fp"] = df['solo']*default_scoring['solo']+df['assists']*default_scoring['ast']+df['sacks']*default_scoring['sacks']+df['interceptions']*default_scoring['interceptions']+df['ffb']*default_scoring['ffb']+df['fr']*default_scoring['fr']+df['sfty']*default_scoring['sfty']+(df['int_td']+df['fb_td'])*default_scoring['td']
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
    #this is for our table headers
    table_headers = ['Name', 'Fantasy Points']
    context = {'tuples':tuples, 'header':header, 'table_headers':table_headers}

    #this appends the context dictionary with the form object
    context['form'] = form

    return render(request, 'defense/test.html', context)

def position_group(request, position):
    #the url will pass in either dl,lb or db. this view will narrow down the positions based on which one it gets
    #and provide a custom header.
    if position == 'dl':
        positions = ['DE','DE/LB','DE/DT','DL','DL/LB','DT','DT/LB']
        header = 'Top 10 Defensive Linemen'
    elif position == 'lb':
        positions = ['DE/LB','DL/LB','DT/LB','LB']
        header = 'Top 10 Linebackers'
    else:
        positions = ['CB','CB/S','DB','S']
        header = 'Top 10 Secondary'
    default_scoring = {'solo':1,'ast':0.5,'sacks':3,'interceptions':3,'ffb':3, 'fr':1, 'td':6, 'sfty':2,}
    #this is pulling all of the team info database
    raw_stats = TeamInfo.objects.all()
    #this gets it so pandas can use it
    stats = raw_stats.values()
    #here we have our pandas dataframe
    df = pd.DataFrame.from_records(stats)
    #gonna narrow this down to just 2019
    df = df[df['year'] == 2019]
    df = df[df['position'].isin(positions)]
    #this puts in our default scoring as a column in the dataframe it is calculated based on the above dictionary and a dataframe of our postgresql database
    df["fp"] = df['solo']*default_scoring['solo']+df['assists']*default_scoring['ast']+df['sacks']*default_scoring['sacks']+df['interceptions']*default_scoring['interceptions']+df['ffb']*default_scoring['ffb']+df['fr']*default_scoring['fr']+df['sfty']*default_scoring['sfty']+(df['int_td']+df['fb_td'])*default_scoring['td']
    #this sorts by fantasy point totals
    df = df.sort_values(['year','fp'], ascending=[False, False])
    #sort out the top 10
    df = df[0:10]
    #list for the top ten scorers ids
    ids = df['player_id_id'].values.tolist()
    #gets the name information for the players
    players = Players.objects.filter(pk__in=ids)
    #now to get the fantasy point totals and the players id for a join
    df = df[['fp', 'solo', 'assists', 'interceptions', 'ffb', 'sacks', 'player_id_id']]
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
    #this is for our table headers
    table_headers = ['Name', 'Fantasy Points', 'Solo Tackles', 'Assisted Tackles', 'Interceptions', 'FFB', 'Sacks']
    context = {'tuples':tuples, 'header':header, 'table_headers':table_headers}


    return render(request, 'defense/position.html', context)

def player_indv(request, player_id):
    player_info = get_object_or_404(Players, pk=player_id)
    team_info = get_list_or_404(TeamInfo.objects.order_by('-year'), player_id=player_id)

    #this pulls all of the stats on file for the current player id
    qs = TeamInfo.objects.filter(player_id=player_id)
    #this gets the values in a format for a pandas dataframe
    q = qs.values()

    #the below DataFrame we can use to generate whatever tables we want,
    df = pd.DataFrame.from_records(q).sort_values(['year'])

    #this creates a dataframe that will show in the players details screen.
    df_table = df[['year','team','age','position','g','gs','interceptions','int_td','pass_def','ffb','fr','fb_td','sacks','solo','assists','tfl','qb_hits','sfty']]
    table = df_table.sort_values(['year'], ascending=[False]).to_html()

    fig = go.Figure()
    #if this is a post request the data must be processed
    if request.method == 'POST':
        #this takes in all of the checked boxes for the graph
        form = Customized_Tables(request.POST)
        #this list will be populated with the categories the user wants plotted
        stat_list = []
        #if the submission is valit the stat_list will populate with the category of each checked box
        if form.is_valid():
            cd = form.cleaned_data
            #if the fantaxy_point mode is checked then it will ignore all the others and make a stacked bar chart
            if cd.get('fantasy_point_mode'):
                #this adds the default scoring settings
                default_scoring = {'solo':1,'ast':0.5,'sacks':3,'interceptions':3,'ffb':3, 'fr':1, 'td':6, 'sfty':2,}
                #this narrows the dataframe to only fields we need for the graph
                df = df[['year','interceptions','int_td','ffb','fr','fb_td','sacks','solo','assists','sfty']]
                #all the below updates the stats so they are expressed in fantasy points
                df['solo'] = df['solo']*default_scoring['solo']
                df['assists'] = df['assists']*default_scoring['ast']
                df['sacks'] = df['sacks']*default_scoring['sacks']
                df['interceptions'] = df['interceptions']*default_scoring['interceptions']
                df['ffb'] = df['ffb']*default_scoring['ffb']
                df['fr'] = df['fr']*default_scoring['fr']
                df['td'] = (df['int_td']+df['fb_td'])*default_scoring['td']
                df['sfty'] = df['sfty']*default_scoring['sfty']
                #this gives us the fields we want plotted on the y axis
                point_categories = ['interceptions','int_td','ffb','fr','fb_td','sacks','solo','assists','sfty']

                #this adds the bars for each year
                for i in point_categories:
                    fig.add_trace(go.Bar(x=df['year'],y=df[i],name=i))
                #this is were the layout is determined
                fig.update_layout(barmode='stack',title="Fantasy Point Chart", xaxis_title="Season", yaxis_title="Fantasy Points", width=850, height=500,
                   xaxis = dict(tickmode = 'linear', dtick = 1), yaxis = dict(tickmode = 'linear', tick0 = 0, dtick = 10) )
            #if fantasy point mode isn't clicked then it will only plot the ones that are checked as a lined scatter plot
            else:
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
                if cd.get('fantasy_points'):
                    default_scoring = {'solo':1,'ast':0.5,'sacks':3,'interceptions':3,'ffb':3, 'fr':1, 'td':6, 'sfty':2,}
                    df["fantasy_points"] = df['solo']*default_scoring['solo']+df['assists']*default_scoring['ast']+df['sacks']*default_scoring['sacks']+df['interceptions']*default_scoring['interceptions']+df['ffb']*default_scoring['ffb']+df['fr']*default_scoring['fr']+df['sfty']*default_scoring['sfty']+(df['int_td']+df['fb_td'])*default_scoring['td']
                    stat_list.append('fantasy_points')

            #this plots all of the categories the user checked
            for i in stat_list:
                fig.add_trace(go.Scatter(x=df['year'],y=df[i],name=i))

                #this adds the axis settings we want
            fig.update_layout(title="Player Stats", xaxis_title="Season", width=850, height=500,
                xaxis = dict(tickmode = 'linear', dtick = 1), yaxis = dict(tickmode = 'linear', tick0 = 0, dtick = 10))

        #this set the html, css, and javascript needed for our graph to the variable plot_div, this can be passed to the template
        plot_div = plot(fig, output_type='div')

    else:
        form = Customized_Tables()

            #this adds the axis settings we want
        fig.update_layout(title="Player Stats", xaxis_title="Season", width=850, height=500,
            xaxis = dict(tickmode = 'linear', dtick = 1), yaxis = dict(tickmode = 'linear', tick0 = 0, dtick = 10))

        #this set the html, css, and javascript needed for our graph to the variable plot_div, this can be passed to the template
        plot_div = plot(fig, output_type='div')

    context = {'player_info': player_info, 'team_info':team_info, 'table':table, 'plot_div': plot_div, 'form':form}

    return render(request, 'defense/detail.html', context)
    #this is returning the players name and stats by year if you follow the url defense/player's_id
    #it is essentially an info page for the player



