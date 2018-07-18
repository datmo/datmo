Visualizing Snapshots
==========================================

In Datmo, :ref:`snapshots` are used as the primary record of state for a project, recording all components of a project state, including files, model weights, environment, configuration, stats, and other metadata. There are three primary ways to assess Snapshots using the CLI:

1. :ref:`view-all-snapshots`
2. :ref:`inspect-a-single-snapshot`
3. :ref:`compare-two-snapshots`


.. _view-all-snapshots:

View all Snapshots within a project
---------------------------------------------------

If you'd like to see a broad overview of all snapshots in the current datmo project, the user can do so with:

    ``$ datmo snapshot ls``

This will return the metadata for all snapshots in a table that resembles the following format:

    .. code-block:: none

        +---------+-------------+-------------------------------------------+-----------------+---------------+-------+
        |    id   |  created at |                 config                    |   stats         |    message    | label |
        +---------+-------------+-------------------------------------------+-----------------+---------------+-------+
        | 30f8366b|  2018-05-16 | {u'selected features': [u'Sex', u'Pclass',|{u'accuracy':    |   auto-ml-2   |  None |
        |         |   03:04:06  |  u'Age', u'Fare', u'Embarked', u'Title',  |   0.8295964}    |               |       |
        |         |             |   u'FarePerPerson', u'FamilySize']}       |                 |               |       |
        | adf76fa7|  2018-05-16 | {u'selected features': [u'Sex', u'Pclass',|{u'accuracy':    |   auto-ml-1   |  None |
        |         |   01:24:53  |  u'Age', u'Fare', u'Embarked',            |   0.8206278}    |               |       |
        |         |             |   u'Fare', u'IsAlone', u'Title']}         |                 |               |       |
        | 30803662|  2018-05-15 | {u'features analyzed': [u'Sex',           |    {}           |     EDA       |  None |
        |         |   23:15:44  |  u'Pclass', u'FamilySize', u'IsAlone',    |                 |               |       |
        |         |             |  u'Embarked', u'Fare', u'Age', u'Title']} |                 |               |       |
        +---------+-------------+-------------------------------------------+-----------------+---------------+-------+

.. _inspect-a-single-snapshot:

Inspect a single Snapshot
---------------------------------------------------

If you'd like to see a detailed view of all properties pertaining to a specific snapshot, use:

    ``$ datmo snapshot inspect <SNAPSHOT_ID>``

This will return a detailed view of the snapshot that resembles the following:

    .. code-block:: none

        Date: Tue Jul 17 15:38:04 2018 -0700
        Session      -> a2084eeaf6a7c66509972ea4f8ca35027721e34e
        Visible      -> True
        Code         -> 1dadd5bbc73822ed90d9061c9003fc2556b9d40b
        Environment  -> 47cc3cee2043f4e9026997e01c53918bad74f28a
        Files        -> 155cc40f0d762712cd115e8262d1e8033aba727c
        Config       -> {u'selected features': [u'Sex', u'Pclass', u'Age', u'Fare', u'Embarked', u'FarePerPerson', u'FamilySize', u'Title']}
        Stats        -> {u'accuracy': 0.8161434977578476}


.. _compare-two-snapshots:

Compare two Snapshots
---------------------------------------------------

There will often be times where you want to see the difference between two snapshots.

This is possible with the following command:

    ``$ datmo snapshot diff <SNAPSHOT_ID_1> <SNAPSHOT_ID_2>``

Resulting in an output resembling the following:

    .. code-block:: none

        Attributes          Snapshot 1                                    Snapshot 2

        id                  9d8e06ae0c8546465c1b0c200f1e84a33c049067  ->  5e476e78b8b480506e117fdf8478c45d28020165
        created_at          Tue Jul 17 15:38:04 2018 -0700            ->  Tue Jul 17 15:30:08 2018 -0700
        message             auto-ml-2                                 ->  auto-ml-1
        label               N/A                                       ->  N/A
        code_id             1dadd5bbc73822ed90d9061c9003fc2556b9d40b  ->  c78873227313f64c3362ee9b30432053036eef68
        environment_id      47cc3cee2043f4e9026997e01c53918bad74f28a  ->  47cc3cee2043f4e9026997e01c53918bad74f28a
        file_collection_id  155cc40f0d762712cd115e8262d1e8033aba727c  ->  155cc40f0d762712cd115e8262d1e8033aba727c