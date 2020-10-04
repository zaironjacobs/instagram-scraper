from instagram_scraper.console_name import __console_name__

descriptor = '  {:<30} {}'
message_help_required_tagname = descriptor.format('', 'required: provide a tag to scrape')
message_help_required_login_username = descriptor.format('', 'required: add a login username')
message_help_required_users_to_remove = descriptor.format('', 'required: add users to remove')
message_help_required_users_n_to_remove = descriptor.format('', 'required: add user numbers to remove')
message_help_required_tags_to_remove = descriptor.format('', 'required: add tags to remove')
message_help_required_tags_n_to_remove = descriptor.format('', 'required: add tag numbers to remove')
message_help_required_max = descriptor.format('', 'required: provide a max number of posts to scrape')
message_help_recommended_max = descriptor.format('', 'recommended: provide a max number of posts to scrape')

args_options = [
    ['--login-username', 'the login username' + '\n'
     + message_help_required_login_username],
    ['--update-users', 'Check all previously scraped users for new posts' + '\n'
     + message_help_recommended_max],
    ['--top-tags', 'scrape top tags' + '\n'
     + message_help_required_tagname],
    ['--recent-tags', 'scrape recent tags' + '\n'
     + message_help_required_tagname],
    ['--max', 'maximum number of posts to scrape' + '\n'
     + message_help_required_max],
    ['--headful', 'display the browser'],
    ['--list-users', 'list all scraped users'],
    ['--list-tags', 'list all scraped tags'],
    ['--remove-users', 'remove user(s)' + '\n'
     + message_help_required_users_to_remove],
    ['--remove-users-n', 'remove user(s) by number' + '\n'
     + message_help_required_users_n_to_remove],
    ['--remove-all-users', 'remove all users'],
    ['--remove-tags', 'remove tag(s)' + '\n'
     + message_help_required_tags_to_remove],
    ['--remove-tags-n', 'remove tag(s) by number' + '\n'
     + message_help_required_tags_n_to_remove],
    ['--remove-all-tags', 'remove all tags'],
    ['--version', 'program version'],
    ['--help', 'show help']
]


def print_help():
    print('usage: ' + __console_name__ + ' [usernames] [options]')
    print('')
    print('options: ')
    for i, argument in enumerate(args_options):
        print(descriptor.format(argument[0], argument[1]))
