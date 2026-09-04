import { mount } from '@vue/test-utils';

import { describe, expect, it, vi } from 'vitest';

import DataLoadState from '#/components/DataLoadState.vue';

vi.mock('#/locales', () => ({
  $t: (key: string) => `t:${key}`,
}));

describe('DataLoadState', () => {
  it('默认渲染插槽内容', () => {
    const wrapper = mount(DataLoadState, {
      slots: { default: '<div class="page-content" />' },
    });
    expect(wrapper.find('.page-content').exists()).toBe(true);
    expect(wrapper.find('.load-error').exists()).toBe(false);
    expect(wrapper.find('.load-skeleton').exists()).toBe(false);
  });

  it('loading 渲染骨架并应用 minHeight', () => {
    const wrapper = mount(DataLoadState, {
      props: { loading: true, minHeight: '320px' },
    });
    const skeleton = wrapper.find('.load-skeleton');
    expect(skeleton.exists()).toBe(true);
    expect(skeleton.attributes('style')).toContain('320px');
  });

  it('error 渲染提示与重试按钮，点击触发 retry', async () => {
    const wrapper = mount(DataLoadState, {
      props: { error: 'pages.err.network' },
    });
    const errorBlock = wrapper.find('.load-error');
    expect(errorBlock.exists()).toBe(true);
    expect(errorBlock.text()).toContain('t:pages.err.network');
    expect(wrapper.text()).toContain('t:pages.common.retry');

    await wrapper.find('button').trigger('click');
    expect(wrapper.emitted('retry')).toHaveLength(1);
  });

  it('error 优先于 loading', () => {
    const wrapper = mount(DataLoadState, {
      props: { error: 'boom', loading: true },
    });
    expect(wrapper.find('.load-error').exists()).toBe(true);
    expect(wrapper.find('.load-skeleton').exists()).toBe(false);
  });
});
