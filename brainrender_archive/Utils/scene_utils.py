import numpy as np
from vedo import Mesh
import random

import brainrender
from brainrender.Utils.camera import check_camera_param
from brainrender.colors import get_random_colors


def parse_add_actors_inputs(actors, name, br_class):
    n = len(actors)
    if name is not None:
        if isinstance(name, str):
            names = [name for i in range(n)]
        elif len(name) != len(actors):
            raise ValueError(
                f"Expected {n} actor names but got {len(name)} while adding actors to scene"
            )
        else:
            names = name
    else:
        names = [None for i in range(n)]

    if br_class is not None:
        if isinstance(br_class, str):
            br_classes = [br_class for i in range(n)]
        elif len(br_class) != len(actors):
            raise ValueError(
                f"Expected {n} actor names but got {len(br_class)} while adding actors to scene"
            )
        else:
            br_classes = br_class
    else:
        br_classes = [None for i in range(n)]

    return actors, names, br_classes


def get_scene_camera(camera, atlas):
    """
        Gets a working camera. 
        In order these alternatives are used:
            - user given camera
            - atlas specific camera
            - default camera
    """
    if camera is None:
        if atlas.default_camera is not None:
            return check_camera_param(atlas.default_camera)
        else:
            return brainrender.CAMERA
    else:
        return check_camera_param(camera)


def get_scene_plotter_settings(jupyter, atlas, verbose):
    """
        Gets settings for vedo Plotter

    """

    if brainrender.WHOLE_SCREEN and not jupyter:
        sz = "full"
    elif brainrender.WHOLE_SCREEN and jupyter:
        if verbose:
            print(
                "Setting window size to 'auto' as whole screen is not available in jupyter"
            )
        sz = "auto"
    else:
        sz = "auto"

    if brainrender.SHOW_AXES:
        if brainrender.AXES_STYLE == 1:
            try:
                ax_idx = atlas.space.axes_order.index("frontal")
            except AttributeError:
                # some custom atlases might not have .space
                axes = 1
            else:
                # make acustom axes dict
                atlas_shape = np.array(atlas.metadata["shape"]) * np.array(
                    atlas.metadata["resolution"]
                )

                z_ticks = [
                    (-v, str(np.abs(v).astype(np.int32)))
                    for v in np.linspace(0, atlas_shape[ax_idx], 10,)
                ]

                # make custom axes dict
                axes = dict(
                    axesLineWidth=3,
                    tipSize=0,
                    xtitle="AP (μm)",
                    ytitle="DV (μm)",
                    ztitle="LR (μm)",
                    textScale=0.8,
                    xTitleRotation=0,
                    xFlipText=True,
                    zrange=np.array([-atlas_shape[2], 0]),
                    zValuesAndLabels=z_ticks,
                )

        elif brainrender.AXES_STYLE != 7:
            raise NotImplementedError(
                "Currently only AXES_STYLE=1 is supported, sorry"
            )
            axes = brainrender.AXES_STYLE
        else:
            # we need to make our custom axes in Render
            axes = 0
    else:
        axes = 0

    return dict(
        size=sz, axes=axes, pos=brainrender.WINDOW_POS, title="brainrender"
    )


def get_cells_colors_from_metadata(color_by_metadata, coords_df, color):
    """
        Get color of each cell given some metadata entry

        :param color_by_metadata: str, column name with metadata info
        :param coords_df: dataframe with cell coordinates and metadata
    """

    if color_by_metadata not in coords_df.columns:
        raise ValueError(
            'Color_by_metadata argument should be the name of one of the columns of "coords"'
        )

    # Get a map from metadata values to colors
    vals = list(coords_df[color_by_metadata].values)
    if len(vals) == 0:
        raise ValueError(
            f"Cant color by {color_by_metadata} as no values were found"
        )
    if not isinstance(
        color, dict
    ):  # The user didn't pass a lookup, generate random
        base_cols = get_random_colors(n_colors=len(set(vals)))
        cols_lookup = {v: c for v, c in zip(set(vals), base_cols)}
    else:
        try:
            for val in list(set(vals)):
                color[val]
        except KeyError:
            raise ValueError(
                'While using "color_by_metadata" with a dictionary of colors passed'
                + ' to "color", not every metadata value was assigned a color in the dictionary'
                + " please make sure that the color dictionary is complete"
            )
        else:
            cols_lookup = color

    # Use the map to get a color for each cell
    color = [cols_lookup[v] for v in vals]

    return color


def get_n_random_points_in_region(atlas, region, N, hemisphere=None):
    """
    Gets N random points inside (or on the surface) of the mesh defining a brain region.

    :param region: str, acronym of the brain region.
    :param N: int, number of points to return.
    """
    if isinstance(region, Mesh):
        region_mesh = region
    else:
        if hemisphere is None:
            region_mesh = atlas._get_structure_mesh(region)
        else:
            region_mesh = atlas.get_region_unilateral(
                region, hemisphere=hemisphere
            )
        if region_mesh is None:
            return None

    region_bounds = region_mesh.bounds()

    X = np.random.randint(region_bounds[0], region_bounds[1], size=10000)
    Y = np.random.randint(region_bounds[2], region_bounds[3], size=10000)
    Z = np.random.randint(region_bounds[4], region_bounds[5], size=10000)
    pts = [[x, y, z] for x, y, z in zip(X, Y, Z)]

    try:
        ipts = region_mesh.insidePoints(pts).points()
    except:
        ipts = region_mesh.insidePoints(
            pts
        )  # to deal with older instances of vedo
    return random.choices(ipts, k=N)
