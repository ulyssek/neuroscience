import numpy as np

import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection


def radar_factory(num_vars, frame='circle'):
    """Create a radar chart with `num_vars` axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle' | 'polygon'}
        Shape of frame surrounding axes.

    """
    # calculate evenly-spaced axis angles
    theta = 2*np.pi * np.linspace(0, 1-1./num_vars, num_vars)
    # rotate theta such that the first axis is at the top
    theta += np.pi/2

    def draw_poly_patch(self):
        verts = unit_poly_verts(theta)
        return plt.Polygon(verts, closed=True, edgecolor='k')

    def draw_circle_patch(self):
        # unit circle centered on (0.5, 0.5)
        return plt.Circle((0.5, 0.5), 0.5)

    patch_dict = {'polygon': draw_poly_patch, 'circle': draw_circle_patch}
    if frame not in patch_dict:
        raise ValueError('unknown value for `frame`: %s' % frame)

    class RadarAxes(PolarAxes):

        name = 'radar'
        # use 1 line segment to connect specified points
        RESOLUTION = 1
        # define draw_frame method
        draw_patch = patch_dict[frame]

        def fill(self, *args, **kwargs):
            """Override fill so that line is closed by default"""
            closed = kwargs.pop('closed', True)
            return super(RadarAxes, self).fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super(RadarAxes, self).plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.concatenate((x, [x[0]]))
                y = np.concatenate((y, [y[0]]))
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(theta * 180/np.pi, labels)

        def _gen_axes_patch(self):
            return self.draw_patch()

        def _gen_axes_spines(self):
            if frame == 'circle':
                return PolarAxes._gen_axes_spines(self)
            # The following is a hack to get the spines (i.e. the axes frame)
            # to draw correctly for a polygon frame.

            # spine_type must be 'left', 'right', 'top', 'bottom', or `circle`.
            spine_type = 'circle'
            verts = unit_poly_verts(theta)
            # close off polygon by repeating first vertex
            verts.append(verts[0])
            path = Path(verts)

            spine = Spine(self, spine_type, path)
            spine.set_transform(self.transAxes)
            return {'polar': spine}

    register_projection(RadarAxes)
    return theta


def unit_poly_verts(theta):
    """Return vertices of polygon for subplot axes.

    This polygon is circumscribed by a unit circle centered at (0.5, 0.5)
    """
    x0, y0, r = [0.5] * 3
    verts = [(r*np.cos(t) + x0, r*np.sin(t) + y0) for t in theta]
    return verts


def example_data():
    #The following data is from the Denver Aerosol Sources and Health study.
    #See  doi:10.1016/j.atmosenv.2008.12.017
    #
    #The data are pollution source profile estimates for five modeled pollution
    #sources (e.g., cars, wood-burning, etc) that emit 7-9 chemical species.
    #The radar charts are experimented with here to see if we can nicely
    #visualize how the modeled source profiles change across four scenarios:
    #  1) No gas-phase species present, just seven particulate counts on
    #     Sulfate
    #     Nitrate
    #     Elemental Carbon (EC)
    #     Organic Carbon fraction 1 (OC)
    #     Organic Carbon fraction 2 (OC2)
    #     Organic Carbon fraction 3 (OC3)
    #     Pyrolized Organic Carbon (OP)
    #  2)Inclusion of gas-phase specie carbon monoxide (CO)
    #  3)Inclusion of gas-phase specie ozone (O3).
    #  4)Inclusion of both gas-phase speciesis present...
    data = {
        'column names':
            ['Sulfate', 'Nitrate', 'EC', 'OC1', 'OC2', 'OC3', 'OP', 'CO', 'O3'],
        'Basecase':
            [[0.88, 0.01, 0.03, 0.03, 0.00, 0.06, 0.01, 0.00, 0.00],
             [0.07, 0.95, 0.04, 0.05, 0.00, 0.02, 0.01, 0.00, 0.00],
             [0.01, 0.02, 0.85, 0.19, 0.05, 0.10, 0.00, 0.00, 0.00],
             [0.02, 0.01, 0.07, 0.01, 0.21, 0.12, 0.98, 0.00, 0.00],
             [0.01, 0.01, 0.02, 0.71, 0.74, 0.70, 0.00, 0.00, 0.00]],
        'With CO':
            [[0.88, 0.02, 0.02, 0.02, 0.00, 0.05, 0.00, 0.05, 0.00],
             [0.08, 0.94, 0.04, 0.02, 0.00, 0.01, 0.12, 0.04, 0.00],
             [0.01, 0.01, 0.79, 0.10, 0.00, 0.05, 0.00, 0.31, 0.00],
             [0.00, 0.02, 0.03, 0.38, 0.31, 0.31, 0.00, 0.59, 0.00],
             [0.02, 0.02, 0.11, 0.47, 0.69, 0.58, 0.88, 0.00, 0.00]],
        'With O3':
            [[0.89, 0.01, 0.07, 0.00, 0.00, 0.05, 0.00, 0.00, 0.03],
             [0.07, 0.95, 0.05, 0.04, 0.00, 0.02, 0.12, 0.00, 0.00],
             [0.01, 0.02, 0.86, 0.27, 0.16, 0.19, 0.00, 0.00, 0.00],
             [0.01, 0.03, 0.00, 0.32, 0.29, 0.27, 0.00, 0.00, 0.95],
             [0.02, 0.00, 0.03, 0.37, 0.56, 0.47, 0.87, 0.00, 0.00]]
             }

    data2 = {
        'column names':
          ["N","NE", "E", "SE", "S", "SO", "O", "NO"],

          'Groupe 1':
          [[0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.01], [0.001, 0.02, 0.001, 0.1, 0.11, 0.001, 0.02, 0.001],[0.03, 0.001, 0.02, 0.04, 0.05, 0.001, 0.01, 0.001], [0.03, 0.001, 0.01, 0.03, 0.05, 0.01, 0.001, 0.001]],
          
          'Groupe 2':
          [[0.001, 0.001, 0.01, 0.001, 0.001, 0.01, 0.001, 0.1], [0.001, 0.01, 0.001, 0.1, 0.11, 0.001, 0.02, 0.001],[0.03, 0.001, 0.02, 0.04, 0.05, 0.001, 0.01, 0.001], [0.03, 0.001, 0.01, 0.03, 0.05, 0.01, 0.001, 0.001]], 
          
          'Groupe 3':
          [[0.1, 0.001, 0.1, 0.001, 0.01, 0.001, 0.01, 0.001], [0.1, 0.001, 0.001, 0.001, 0.01, 0.001, 0.01, 0.001],[0.03, 0.001, 0.02, 0.04, 0.05, 0.001, 0.01, 0.001], [0.03, 0.001, 0.01, 0.03, 0.05, 0.01, 0.001, 0.001]], 
          
          'Groupe 4':
          [[0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001], [0.001, 0.01, 0.001, 0.001, 0.1, 0.001, 0.01, 0.001],[0.03, 0.001, 0.02, 0.04, 0.05, 0.001, 0.01, 0.001], [0.03, 0.001, 0.01, 0.03, 0.05, 0.01, 0.001, 0.001]]




    }
    return data2


def plot_diagram(data,card=False):

  try:
    spoke_labels = data.pop('column names')
  except:
    pass
  
  radar = Radar(card)
  radar.add_dict(data)
  radar.plot()

class Radar():

  ##################################################################
  ## CLASS VARS

  CARD_LABELS     = ["N","NE","E","SE","S","SO","O","NO"]
  PLOTTING_LIMIT  = 4
  
  ##################################################################
  ## BUILDING FUNCTIONS

  def __init__(self, card=True,labels=None):
    self._card = True
    self._data = {}
    if card:
      self._labels = self.CARD_LABELS
    elif labels is not None:
      self._labels = labels
    else:
      self._labels = range(10)
      

  def add_data(self, name, data, force=False):
    if name in self._data.keys() and not force:
      raise Exception("name's already used, please use force=True")
    self._data[name] = data

  
  def add_dict(self, data, force=False):
    for key in data.keys():
      self.add_data(key, data[key], force)

  @classmethod
  def RadarsFromList(cls, data_list):
    size = len(data_list[0])
    zero = map(lambda x : 0.001, range(size))
    temp            = {}
    count           = 1
    radars          = []
    plotting_limit  = cls.PLOTTING_LIMIT
    for i in xrange(len(data_list)):
      chaine = "Neuron %s" % (i+1)
      temp[chaine] = [data_list[i],zero]
      count += 1
      if count == (plotting_limit +1):
        radar = Radar()
        radar.add_dict(temp)
        radars.append(radar)
        count = 1
        temp = {}
    if temp:
      radar = Radar()
      radar.add_dict(temp)
      radars.append(radar)
    return radars

    

  ##################################################################
  ## GETTING FUNCTIONS 
  
  def get_nb_fig(self):
    return len(self._data)

  def get_data_size(self):
    return len(self._data[self._data.keys()[0]][0])

  ##################################################################
  ## PLOTING FUNCTIONS

  def plot(self,legend=True,fig_title=None):
    theta = radar_factory(self.get_data_size(), frame='polygon')

    fig = plt.figure(figsize=(9, 9))
    fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)

    colors = ['b', 'r', 'g', 'm', 'y']
    # Plot the four cases from the example data on separate axes
    for n, title in enumerate(self._data.keys()):
        ax = fig.add_subplot(2, 2, n+1, projection='radar')
        plt.rgrids([0.02, 0.04, 0.06, 0.08])
        ax.set_title(title, weight='bold', size='medium', position=(0.5, 1.1),
                     horizontalalignment='center', verticalalignment='center')
        for d, color in zip(self._data[title], colors):
            ax.plot(theta, d, color=color)
            ax.fill(theta, d, facecolor=color, alpha=0.25)
        ax.set_varlabels(self._labels)

    if legend:
      self.plot_legend()
    if fig_title is not None:
      self.plot_title(fig_title)
    plt.show()

  def plot_legend(self):
    # add legend relative to top-left plot
    plt.subplot(2, 2, 1)
    labels = ('Neuron 1', 'Neuron 2', 'Neuron 3', 'Neuron 4')
    legend = plt.legend(labels, loc=(0.9, .95), labelspacing=0.1)
    plt.setp(legend.get_texts(), fontsize='small')

  def plot_title(self,title):
    plt.figtext(0.5, 0.965, title,
                ha='center', color='black', weight='bold', size='large')
