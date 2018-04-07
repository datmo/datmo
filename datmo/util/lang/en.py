class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

MESSAGES = {
    "general.line": "==============================================================",
    "setup.init_project": bcolors.OKGREEN + bcolors.BOLD + "Initializing project {name} @ ({path}) " + bcolors.ENDC,
    "setup.pulling_datmo_project" : bcolors.HEADER + "Pulling information from the Datmo project url and adding it to local..." + bcolors.ENDC,
    "setup.internet_required": bcolors.WARNING + "warning: internet connectivity doesn't exist" + bcolors.ENDC,
    "setup.git_installed": bcolors.WARNING + "warning: git isn't setup. please install git" + bcolors.ENDC,
    "setup.logged_in_status": bcolors.WARNING + "warning: user is not logged into datmo. use `datmo setup` or `datmo login` to login" + bcolors.ENDC,
    "setup.datmo_token_missing": bcolors.WARNING + "warning: user is not logged into datmo. use `datmo setup` or `datmo login` to login" + bcolors.ENDC,
    "setup.datmo_pulling_project": bcolors.HEADER + "Pulling information from the Datmo project url and adding it to local..." + bcolors.ENDC,
    "setup.datmo_project_update": bcolors.HEADER + "Update Datmo project" + bcolors.ENDC,
    "setup.datmo_project_name": bcolors.BOLD + "---> Enter name for the Datmo project" + bcolors.ENDC,
    "setup.datmo_project_description": bcolors.BOLD + "---> Enter name for the Datmo project" + bcolors.ENDC,
    "setup.datmo_project_git_url": bcolors.BOLD + "---> Enter remote git url for the Datmo project" + bcolors.ENDC,
    "setup.datmo_project_update_confirm": bcolors.BOLD + "---> Is it okay?" + bcolors.ENDC,
    "setup.datmo_project_update_abort": u'\u274c' + "  Your changes have been aborted!",
    "setup.datmo_project_update_success": bcolors.OKGREEN + bcolors.BOLD + u'\u2713' + " You have successfully re-initialized your local Datmo project here %s" + bcolors.ENDC,
    "setup.datmo_project_create": bcolors.HEADER + "Creating a new Datmo project" + bcolors.ENDC,
    "setup.datmo_project_repo_setup": bcolors.WARNING + " Creating public repository on GitHub. Please change repo settings if you would like to." + bcolors.ENDC,
    "general.echo.input" : "You entered: %s",
    "test.dict.replacements" : "{foo} - {bar}",
    "test.tuple.replacements" : "%s, %s",
    "cli.exception": "An exception occured: %s"
}

def get_messages():
  return MESSAGES
