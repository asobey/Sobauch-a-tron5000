from tabulate import tabulate
import AutoLeague_ESPN.Unused_Modules.team_table_parse as team_table_parse

POSITIONS = ['QB', 'K', 'D/ST', 'TE', 'RB', 'WR']


def optimize(team_table):
    team_dic = make_team_dic(team_table, POSITIONS)

    ranked_dic = rank_team_dic(team_dic, 'ESPN')

    new_ranked_dic = add_multi_pos_chart(ranked_dic)

    optimal_position_chart = optimize_position_chart(new_ranked_dic)

    return optimal_position_chart


def make_team_dic(table, positions):
    team_dic = {}  # Making a dictionary of the team
    for pos in positions:
        pos_true = table.index[table['POS'].str.contains(pos)].values  # list of true values by row number
        #print(pos + ' : ' + str(pos_true))
        team_dic[pos] = table.loc[pos_true]
        #print(tabulate(team_dic[pos], headers='keys', tablefmt='psql'))
    return team_dic


def rank_team_dic(t_dic, rank_by):
    if rank_by == 'ESPN':
        return rank_team_dic_by_ESPN(t_dic)


def rank_team_dic_by_ESPN(t_dic):
    rank_dic = {}
    for pos in t_dic:
        try:
            rank_dic[pos] = t_dic[pos].sort_values('PROJ', ascending=False)
            print(tabulate(rank_dic[pos], headers='keys', tablefmt='psql'))
        except:
            print('FAILED!!!!!!!!!!!!!!!!!!!!!!')
            print('at: ' + str(pos))
    return rank_dic


def add_multi_pos_chart(r_dic):
    '''This function combined the remaining (not top 2 in positions) WR/RB/TE into two groups: best WR/RB and best remainder'''
    r_dic['REMAINDER'] = r_dic['RB'].iloc[2:].append(r_dic['WR'].iloc[2:]).append(r_dic['TE'].iloc[1:])

    r_dic['REMAINDER'] = r_dic['REMAINDER'].sort_values('PROJ', ascending=False)
    print('REMAINDER:')
    print(tabulate(r_dic['REMAINDER'], headers='keys', tablefmt='psql'))

    if r_dic['REMAINDER']['POS'].iloc[0] == 'TE':
        r_dic['RB/WR'] = r_dic['REMAINDER'].drop(r_dic['REMAINDER'].index[2:]).drop(r_dic['REMAINDER'].index[0])
        r_dic['FLEX'] = r_dic['REMAINDER'].drop(r_dic['REMAINDER'].index[1:])
    else:
        r_dic['RB/WR'] = r_dic['REMAINDER'].drop(r_dic['REMAINDER'].index[1:])
        r_dic['FLEX'] = r_dic['REMAINDER'].drop(r_dic['REMAINDER'].index[2:]).drop(r_dic['REMAINDER'].index[0])
    print('RB/WR:')
    print(tabulate(r_dic['RB/WR'], headers='keys', tablefmt='psql'))
    print('FLEX:')
    print(tabulate(r_dic['FLEX'], headers='keys', tablefmt='psql'))
    return r_dic


def optimize_position_chart(ranked_dic):
    """Create dictionary of optimized position chart"""
    opt_pos_chart = {}
    opt_pos_chart[0] = ranked_dic['QB']['ID'].iloc[0]
    opt_pos_chart[1] = ranked_dic['RB']['ID'].iloc[0]
    opt_pos_chart[2] = ranked_dic['RB']['ID'].iloc[1]
    opt_pos_chart[3] = ranked_dic['RB/WR']['ID'].iloc[0]
    opt_pos_chart[4] = ranked_dic['WR']['ID'].iloc[0]
    opt_pos_chart[5] = ranked_dic['WR']['ID'].iloc[1]
    opt_pos_chart[6] = ranked_dic['TE']['ID'].iloc[0]
    opt_pos_chart[14] = ranked_dic['FLEX']['ID'].iloc[0]
    opt_pos_chart[7] = ranked_dic['D/ST']['ID'].iloc[0]
    opt_pos_chart[8] = ranked_dic['K']['ID'].iloc[0]
    return opt_pos_chart


def optimize_position_table(team_table, opt_pos_chart):
    #opt_pos_table = pd.dataframe()
    first = True
    for key, value in opt_pos_chart.items():
        if first == True:
            opt_pos_table = team_table.loc[team_table['ID'] == value]
            first = False
        else:
            opt_pos_table = opt_pos_table.append(team_table.loc[team_table['ID'] == value])
    return opt_pos_table

def handle_multi_spot_anomoly(team_table, opt_pos_chart):
    '''The ESPN website does not allow for player in RB1 slot to move to RB1 and vice-versa. This is also true for WR1
    and WR2. This function can only handle leagues with 2 RBs and/or 2 WR2. Two QB or any other multi spot positions
    with throw an exception at the end.'''

    # Only need to check for RB1(1) and WR1(3). Error cannot occur with RB2(2) or WR2(4) positions
    for key, value in opt_pos_chart.items():
        if key == 1 and team_table['HERE'].loc[team_table['ID'] == value].item() == 2:
            temp_id = opt_pos_chart[1]
            opt_pos_chart[1] = opt_pos_chart[2]
            opt_pos_chart[2] = temp_id
        if key == 3 and team_table['HERE'].loc[team_table['ID'] == value].item() == 4:
            temp_id = opt_pos_chart[3]
            opt_pos_chart[3] = opt_pos_chart[4]
            opt_pos_chart[4] = temp_id
    return opt_pos_chart

if __name__ == '__main__':
    source_file_locations = '..\\offline_webpages\\'
    source_file_name = 'front_page_source'

    team_table = team_table_parse.create_team_table(source_file_locations, source_file_name)
    team_table_parse.print_table(team_table)

    #print(team_table.sort_values('PROJ', ascending=False))

    team_dic = make_team_dic(team_table, POSITIONS)

    ranked_dic = rank_team_dic(team_dic, 'ESPN')

    for pos in POSITIONS:
        #print(pos + ': UNRANKED TABLE')
        #print(tabulate(team_dic[pos], headers='keys', tablefmt='psql'))
        import time
        time.sleep(.5)
        print(pos + ': RANKED TABLE')
        try:
            print(tabulate(ranked_dic[pos], headers='keys', tablefmt='psql'))
        except:
            pass

    new_ranked_dic = add_multi_pos_chart(ranked_dic)


    optimal_position_chart = optimize_position_chart(new_ranked_dic)
    optimal_position_chart = handle_multi_spot_anomoly(team_table, optimal_position_chart)

    print('OPTIMAL POSITION CHART:')
    print(optimize_position_chart)

    optimal_position_table = optimize_position_table(team_table, optimal_position_chart)
    print(tabulate(optimal_position_table, headers='keys', tablefmt='psql'))


    #Check with player are in place:
    for key, value in optimal_position_chart.items():
        print(f'HERE: {key}, ID: {value}')
        #print(team_table['ID'].loc[team_table['HERE'] == key])
        if team_table['ID'].loc[team_table['HERE'] == key].item() == value:
            print(f'Spot: {key} already filled with player: {value}')
        else:
            print(f'+++++++++++++++++++++++++++++++++++++++++++++++Player: {value} needs to be moved to: {key}++++++++')
"""
Logic:

-Take Top 
    -QB
    -2X RB
    -2X WR
    -TE
    -D/ST
    -K
    -Remaining WR/RB
    -Remaining WR/RB/TE
"""