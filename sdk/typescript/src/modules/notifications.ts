import * as NotificationsType from "../types/notifications";
import { AxiosResponse } from "axios";
import { Connection } from "../client/connection";
import { BaseController } from "../utils/baseController";
import { RequestConfig } from "../utils/globalTypes";

export class NotificationsMe extends BaseController {
    constructor(conn: Connection, token?: string) {
        super(conn, token);
    }
    /** GET /notifications/me/ */
    async notifications_me_list(config?: RequestConfig<NotificationsType.NotificationsMeRequestParams>
    ): Promise<AxiosResponse<NotificationsType.NotificationsMeGetResponseData>> {
        return await this.axiosGet(`/notifications/me/`, config);
    }
}

export class NotificationsOpened extends BaseController {
    constructor(conn: Connection, token?: string) {
        super(conn, token);
    }
    /** GET /notifications/opened/ */
    async notifications_opened_retrieve(config?: RequestConfig<NotificationsType.NotificationsOpenedRequestParams>
    ): Promise<AxiosResponse<NotificationsType.NotificationsOpenedGetResponseData>> {
        return await this.axiosGet(`/notifications/opened/`, config);
    }
}

export class NotificationsViewed extends BaseController {
    constructor(conn: Connection, token?: string) {
        super(conn, token);
    }
    /** GET /notifications/viewed/ */
    async notifications_viewed_retrieve(config?: RequestConfig
    ): Promise<AxiosResponse<NotificationsType.NotificationsViewedGetResponseData>> {
        return await this.axiosGet(`/notifications/viewed/`, config);
    }
}

export class NotificationsController extends BaseController {
    public readonly me: NotificationsMe;
    public readonly opened: NotificationsOpened;
    public readonly viewed: NotificationsViewed;

    constructor(connection: Connection, token?: string) {
        super(connection, token);
        this.me = new NotificationsMe(this.conn);
        this.opened = new NotificationsOpened(this.conn);
        this.viewed = new NotificationsViewed(this.conn);
    }
    
    /** GET /notifications/ */
    async list(config?: RequestConfig<NotificationsType.NotificationsListRequestParams>
    ): Promise<AxiosResponse<NotificationsType.NotificationsListResponseData>> {
        return await this.axiosGet(`/notifications/`, config);
    }
    
    /** POST /notifications/ */
    async create(data: NotificationsType.NotificationsCreateRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<NotificationsType.NotificationsCreateResponseData>> {
        return await this.axiosPost(`/notifications/`, data, config);
    }
    
    /** GET /notifications/{id}/ */
    async retrieve(id: string, config?: RequestConfig
    ): Promise<AxiosResponse<NotificationsType.NotificationsRetrieveResponseData>> {
        return await this.axiosGet(`/notifications/${id}/`, config);
    }
    
    /** PUT /notifications/{id}/ */
    async update(id: string, data: NotificationsType.NotificationsUpdateRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<NotificationsType.NotificationsUpdateResponseData>> {
        return await this.axiosPut(`/notifications/${id}/`, data, config);
    }
    
    /** PATCH /notifications/{id}/ */
    async partialUpdate(id: string, data: NotificationsType.NotificationsPartialupdateRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<NotificationsType.NotificationsPartialupdateResponseData>> {
        return await this.axiosPatch(`/notifications/${id}/`, data, config);
    }
    
    /** DELETE /notifications/{id}/ */
    async delete(id: string, config?: RequestConfig
    ): Promise<AxiosResponse<any>> {
        return await this.axiosDelete(`/notifications/${id}/`, config);
    }
    
}