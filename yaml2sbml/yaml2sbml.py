import argparse
import warnings
import os

import libsbml as sbml
import yaml

from . import yaml2PEtab


def yaml2sbml(yaml_file: str,
              output_dir: str,
              model_name: str,
              petab: bool = True):
    """
    Takes in a yaml file with the ODE specification, parses it, converts it into SBML format, and writes the SBML file.

    Arguments:
        yaml_file : path to the yaml file with the ODEs specification
        output_dir: path the output file(s) are be written out
        model_name: name of SBML model (e.g. lokta_volterra leads to a model named lokta_volterra.xml)
        petab: flag, if the PEtab observable/parameter tables should be generated as well

    Returns:

    Raises:

    """

    if model_name.endswith('.xml'):
        sbml_file = os.path.join(output_dir, model_name)
    else:
        sbml_file = os.path.join(output_dir, model_name + '.xml')

    sbml_as_string = parse_yaml(yaml_file, output_dir, petab)

    # write sbml file
    with open(sbml_file, 'w') as f_out:
        f_out.write(sbml_as_string)


def parse_yaml(yaml_file: str, output_dir: str, petab: bool) -> str:
    """
    Takes in a yaml file with the specification of ODEs, parses it, and returns the corresponding SBML string.

    Arguments:
        yaml_file: path to the yaml file with the ODEs specification
        output_dir: path to the directory, where the output is written
        petab: flag, that indicates weather petab files should be written

    Returns:
        sbml_string: a string containing the ODEs in SBML format

    Raises:
        SystemExit
    """
    try:
        document = sbml.SBMLDocument(3, 1)
    except ValueError:
        raise SystemExit('Could not create SBMLDocument object')

    model = document.createModel()
    model = _create_compartment(model)

    yaml_dic = _load_yaml_file(yaml_file)
    _convert_yaml_blocks_to_sbml(model, yaml_dic)

    if petab:
        yaml2PEtab.create_petab_from_yaml(yaml_dic, output_dir)

    sbml_string = sbml.writeSBMLToString(document)

    return sbml_string


def _create_compartment(model: sbml.Model):
    """
    Creates a default compartment for the model.
    We don't support multiple compartments at the moment.

    Arguments:
        model: SBML model

    Returns:
        model: SBML model with added compartment

    Raises:

    """
    c = model.createCompartment()
    c.setId('Compartment')
    c.setConstant(True)
    c.setSize(1)

    return model


def _load_yaml_file(yaml_file: str) -> dict:
    """
    Loads yaml file and returns the resulting dictionary.

    Arguments:
        yaml_file: SBML model

    Returns:
        yaml_dic: dictionary with parsed yaml file contents

    Raises:

    """
    with open(yaml_file, 'r') as f_in:
        yaml_contents = f_in.read()
        yaml_dic = yaml.full_load(yaml_contents)

    return yaml_dic


def _convert_yaml_blocks_to_sbml(model: sbml.Model, yaml_dic: dict):
    """
    Converts each block in the yaml dictionary to SBML.

    Arguments:
        model: SBML model
        yaml_dic: dictionary with yaml contents

    Returns:
        model: SBML model with added entities

    Raises:

    """
    function_dict = {'time': read_time_block,
                     'parameters': read_parameters_block,
                     'states': read_states_block,
                     'assignments': read_assignments_block,
                     'functions': read_functions_block,
                     'observables': read_observables_block,
                     'odes': read_odes_block,
                     'events': read_events_block}

    for block in yaml_dic:
        function_dict[block](model, yaml_dic[block])

    return model


def read_time_block(model: sbml.Model, time_dic: dict):
    """
    Reads and processes the time block.
    If time units are not given they're set to seconds.

    Arguments:
        model: SBML model to which the rate rule will be added.
        time_dic: a dictionary with the time block in the ODE yaml file.

    Returns:

    Raises:

    """
    create_time(model, time_dic['variable'])


def create_time(model: sbml.Model, time_var: str):
    """
    Creates the time variable, add assignment to 'time'

    Arguments:
        model: the SBML model to which the species will be added.
        time_var: str, the time variable

    Returns:

    Raises:

    """
    time_parameter = model.createParameter()
    time_parameter.setId(time_var)
    time_parameter.setName(time_var)
    time_parameter.setConstant(False)

    time_assignment = model.createAssignmentRule()
    time_assignment.setVariable(time_var)
    time_assignment.setMath(sbml.parseL3Formula('time'))


def read_parameters_block(model: sbml.Model, parameter_list: list):
    """
    Reads and processes the parameters block in the ODE yaml file.
    In particular, it reads the parameters and adds them to the given SBML model.
    The expected format for parameter definition is
    {'parameterId': <parameterId>, 'nominalValue': <nominalValue>}

    Arguments:
        model: the SBML model
        parameter_list: block containing the parameter definitions

    Returns:

    Raises:

    """
    for parameter_def in parameter_list:
        create_parameter(model, parameter_def['parameterId'], parameter_def['nominalValue'])


def create_parameter(model: sbml.Model, parameter_id: str, value: str):
    """
    Creates a parameter and adds it to the given SBML model.
    Units are set as dimensionless by default.

    Arguments:
        model: the SBML model to which the parameter will be added.
        parameter_id: the parameter ID
        value: the parameter value

    Returns:

    Raises:

    """
    k = model.createParameter()
    k.setId(parameter_id)
    k.setName(parameter_id)
    k.setConstant(True)
    k.setValue(float(value))

    k.setUnits('dimensionless')


def read_states_block(model: sbml.Model, state_list: list):
    """
    Reads and processes the states block in the ODE yaml file.
    In particular, it reads the states and adds them to the given SBML file as species.
    The expected format of a state definition is:
    {'stateId': <stateId>, 'initialValue': <initialValue>}

    Arguments:
        model: the SBML model
        state_list: a list of dictionaries where each entry is a state definition

    Returns:

    Raises:

    """
    for state_def in state_list:
        create_species(model, state_def['stateId'], state_def['initialValue'])


def create_species(model: sbml.Model, species_id: str, initial_amount: str):
    """
    Creates a species and adds it to the given SBML model.
    Units are set as dimensionless by default.

    Arguments:
        model: the SBML model to which the species will be added.
        species_id: the species ID
        initial_amount: the species initial amount

    Returns:
        s: the SBML species

    Raises:

    """
    s = model.createSpecies()
    s.setId(species_id)
    s.setInitialAmount(float(initial_amount))
    s.setConstant(False)
    s.setBoundaryCondition(False)
    s.setHasOnlySubstanceUnits(False)
    s.setCompartment('Compartment')

    s.setSubstanceUnits('dimensionless')

    return s


def read_assignments_block(model: sbml.Model, assignment_list: list):
    """
    Reads and processes the assignments block in the ODE yaml file.
    In particular, it reads the assignments and adds them to the given SBML file.
    The expected format of a state definition is:
    {'assignmentId': <assignmentId>, 'formula': <formula>}

    This is used to assign a formula (probably time-dependent) to a variable.

    Arguments:
        model: the SBML model
        assignment_list: a list of dictionaries where each entry is an assignment definition

    Returns:

    Raises:

    """
    for assignment_def in assignment_list:
        create_assignment(model, assignment_def['assignmentId'], assignment_def['formula'])


def create_assignment(model: sbml.Model, assignment_id: str, formula: str):
    """
    Creates an  assignment rule, that assigns id to formula.

    Arguments:
        model: SBML model to which the assignment rule will be added.
        assignment_id: str, the id of the assignment rule
        formula: str: contains the equation for the assignment rule
    Returns:

    Raises:

    """
    assignment_parameter = model.createParameter()
    assignment_parameter.setId(assignment_id)
    assignment_parameter.setName(assignment_id)
    assignment_parameter.setConstant(False)
    assignment_parameter.setUnits('dimensionless')

    assignment_rule = model.createAssignmentRule()
    assignment_rule.setVariable(assignment_id)
    assignment_rule.setMath(sbml.parseL3Formula(formula))


def read_functions_block(model: sbml.Model, functions_list: list):
    """
    Reads and processes the functions block in the ODE yaml file.
    In particular, it reads the functions and adds them to the given SBML file as functionDefinitions.
    The expected format of a function definition is:
    {'functionId': <functionId>, 'arguments': <arguments>,  'formula' : <formula>}

    Arguments:
        model: a SBML model
        functions_list: a list of dictionaries where each entry is a function definition

    Returns:

    Raises:

    """
    for function_def in functions_list:
        create_function(model, function_def['functionId'], function_def['arguments'], function_def['formula'])


def create_function(model: sbml.Model, function_id: str, arguments: str, formula: str):
    """
    Creates a functionDefinition and adds it to the given SBML model.

    Arguments:
        model: SBML model to which the function will be added.
        function_id: the function id/name
        arguments: the arguments of the function (species AND parameters)
        formula: the formula of the function

    Returns:

    Raises:

    """
    f = model.createFunctionDefinition()
    f.setId(function_id)
    math = sbml.parseL3Formula('lambda(' + arguments + ', ' + formula + ')')
    f.setMath(math)


def read_odes_block(model: sbml.Model, odes_list: list):
    """
    Reads and processes lines in the odes block in the ODE yaml file.
    In particular, it reads the odes and adds them to the given SBML file as rateRules.
    The expected format of an ode definition is:
    {'state': <state_variable>, 'rightHandSide' : <right_hand_side>}

    Arguments:
        model: a SBML model
        odes_list: block of ODE definitions

    Returns:

    Raises:

    """
    for ode_def in odes_list:
        create_rate_rule(model, ode_def['state'], ode_def['rightHandSide'])


def create_rate_rule(model: sbml.Model, species: str, formula: str):
    """
    Creates a SBML rateRule for a species and adds it to the given model.
    This is where the ODEs from the text file are encoded.

    Arguments:
        model: SBML model to which the rate rule will be added.
        species: the species name of the ODE
        formula: the right-hand-side of the ODE

    Returns:

    Raises:

    """
    r = model.createRateRule()
    r.setId('d/dt_' + species)
    r.setVariable(species)
    math_ast = sbml.parseL3Formula(formula)
    r.setMath(math_ast)


def read_observables_block(model, observable_list: list):
    """
    Reads an processes the observables block in the ODE yaml file.
    In particular it generates the Observables in the SBML file.
    The expected format is: {'id': <observable_id>, 'formula': <observable_formula>}

    Arguments:
        model: SBML model (libsbml)
        observable_list: observables block containing all observable definitions.

    Returns:

    Raises:

    """
    try:
        for observable_def in observable_list:
            create_observable(model, observable_def['observableId'], observable_def['observableFormula'])
    except TypeError:
        pass


def create_observable(model, observable_id: str, formula: str):
    """
    Creates a parameter with the name observable_id and an assignment rule, that assigns the parameter to
    the equation given in formula.
    Units are set as dimensionless by default.

    Arguments:
        model: SBML model to which the rate rule will be added.
        observable_id: str, the id of the observable
        formula: str: contains the equation for the observable

    Returns:

    Raises:

    """
    obs_param = model.createParameter()
    obs_param.setId('observable_' + observable_id)
    obs_param.setName(observable_id)
    obs_param.setConstant(False)
    obs_param.setUnits('dimensionless')

    obs_assignment_rule = model.createAssignmentRule()
    obs_assignment_rule.setVariable('observable_' + observable_id)
    obs_assignment_rule.setMath(sbml.parseL3Formula(formula))


def read_noise_block(model, line):
    warnings.warn('Noise not supported yet')


# TODO read_events_block
def read_events_block(model: sbml.Model, events_list: list):
    warnings.warn('Events not supported yet')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Takes in an ODE model in .yaml and converts it to SBML.')
    parser.add_argument('yaml_file', type=str)
    parser.add_argument('output_dir', type=str)
    parser.add_argument('model_name', type=str)
    parser.add_argument('petab_output', type=str)

    args = parser.parse_args()

    print(f'Path to yaml file: {args.yaml_file}')
    print(f'Output directory: {args.model_name}')
    print(f'Path to sbml file: {args.model_name}')
    if 'y' in args.petab_output:
        print('PEtab observable/parameter tables are created.')
    print('Converting...')

    yaml2sbml(args.yaml_file,
              args.output_dir,
              args.model_name,
              'y' in args.petab_output)
